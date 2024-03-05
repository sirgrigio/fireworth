import datetime
from functools import cmp_to_key
import re
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
from typing import Dict, List, NamedTuple, Set

from beancount import loader
from beancount.core.amount import add as add_amounts, sub as sub_amounts
from beancount.core.data import Amount, Meta
from beancount.core.data import Posting as BPosting
from beancount.core.data import Transaction as BTransaction

from src.modules.ynab.api.models.transactions import \
    Subtransaction as YSubtransaction
from src.modules.ynab.api.models.transactions import \
    Transaction as YTransaction

from .mappings.accounts import map_account
from .mappings.categories import map_category
from .mappings.payees import map_inflow
from .parsing.utils import travel_name_to_tag
from .parsing.memo_parsers import memo_parser


class YNABtoPostingConverter(ABC):

    def __init__(self, transaction: YTransaction | YSubtransaction) -> None:
        self.txn = transaction
        self.memo_parser = memo_parser(self.txn.memo)

    @abstractmethod
    def convert(self) -> List[BPosting]:
        ...

    @staticmethod
    def _make_posting(account: str, ynab_amount: int, currency: str='EUR', precision=2) -> List[BPosting]:
        amount = Decimal(ynab_amount/1000).quantize(Decimal(10)**-precision)
        return BPosting(account, Amount(amount, currency), None, None, None, None)

    @staticmethod
    def cmp_postings(p1: BPosting, p2: BPosting) -> int:
        if p1.units.number < 0 or p2.units.number < 0:
            return p1.units.number - p2.units.number
        else:
            return -1 if p1.account <= p2.account else 1


class TransferConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if (self.txn.transfer_transaction_id is not None
            and self.txn.account_name != 'Investments'
            and self.txn.payee_name != 'Transfer : Investments'):
            a_from = [map_account(self.txn.account_name)]
            a_to = [map_account(self.txn.payee_name.split(':')[1].strip())]
            recipients = self.memo_parser.extract_recipients()
            if recipients:
                if self.txn.account_name == 'Lending':
                    a_from = [f'{a_from[0]}:{r}' for r in recipients]
                if self.txn.payee_name == 'Transfer : Lending':
                    a_to = [f'{a_to[0]}:{r}' for r in recipients]
            return [
                *[self._make_posting(a, self.txn.amount/len(a_from)) for a in a_from],
                *[self._make_posting(a, -self.txn.amount/len(a_to)) for a in a_to]
            ]
        return None


class InflowConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if self.txn.category_name == 'Inflow: Ready to Assign' and not self.txn.transfer_account_id:
            a_from, a_to = map_inflow(self.txn.payee_name)(self.txn.account_name)
            return [
                self._make_posting(a_from, -self.txn.amount),
                self._make_posting(a_to, self.txn.amount)
            ]
        return None

class ExpenseConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if (self.txn.category_name != 'Inflow: Ready to Assign'
            and self.txn.transfer_account_id is None):
            return [
                self._make_posting(map_account(self.txn.account_name), self.txn.amount),
                self._make_posting(map_category(self.txn.category_name), -self.txn.amount)
            ]
        return None


class YNABBeanifier(ABC):

    def __init__(self, transaction: YTransaction):
        self.txn = transaction
        self.converters: List[YNABtoPostingConverter] = [
            TransferConverter,
            InflowConverter,
            ExpenseConverter,
        ]
        self.memo_parser = memo_parser(self.txn.memo)

    @abstractmethod
    def beanify(self) -> NamedTuple:
        ...

    @staticmethod
    def merge(postings: List[BPosting]) -> List[BPosting]:
        account_postings: Dict[str, List[BPosting]] = {}
        for curr in postings:
            if not curr.account in account_postings:
                account_postings[curr.account] = [curr]
            else:
                updated = []
                prevs = account_postings[curr.account]
                for elem in prevs:
                    if elem.units.currency == curr.units.currency:
                        updated.append(BPosting(
                            elem.account,
                            add_amounts(elem.units, curr.units),
                            None, None, None, None
                        ))
                        break
                    else:
                        updated.append(elem)
                account_postings[curr.account] = updated
        result = []
        for v in account_postings.values():
            result += v
        return sorted(result, key=cmp_to_key(YNABtoPostingConverter.cmp_postings))

    def _make_postings(self) -> List[BPosting]:
        postings = []
        for t in (
            self.txn.subtransactions if self.txn.subtransactions else [self.txn]
        ):
            for c in self.converters:
                new_postings = c(t).convert()
                if new_postings:
                    postings += new_postings
        return self.merge(postings)

    @staticmethod
    def _make_transaction(
            date: datetime.date,
            payee: str,
            flag: str='*',
            narration: str=None,
            tags: Set[str]=[],
            meta: Meta={},
            links: Set[str]=[],
            postings: List[BPosting]=[],
            ) -> NamedTuple:
        return BTransaction(meta, date, flag, payee, narration, tags, links, postings)


class InflowBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        if self.txn.payee_name == 'Inflow: Ready to Assign':
            return self._make_transaction(
                self.txn.date,
                self.txn.payee_name.strip(),
                postings=self._make_postings()
            )
        return None


class TransferBeanifier(YNABBeanifier):

    def __init__(self, transaction: YTransaction):
        super().__init__(transaction)

    def beanify(self) -> NamedTuple:
        if (self.txn.transfer_transaction_id is not None
            and self.txn.account_name != 'Investments'
            and self.txn.payee_name != 'Transfer : Investments'):
            payee = self.memo_parser.extract_payee()
            tags = self.memo_parser.extract_tags()
            postings = self._make_postings()
            is_payment = any([p.account.startswith('Liabilities') for p in postings])
            is_payback = any([p.account.startswith('Assets:Lending') and p.units.number < 0 for p in postings])
            if not payee:
                if is_payment:
                    payee = 'Payment'
                elif is_payback:
                    payee = 'Payback'
                else:
                    payee = 'Transfer'
            if is_payback:
                tags.add('payback')
            return self._make_transaction(
                self.txn.date,
                payee=payee,
                narration=self.memo_parser.extract_narration(),
                tags=tags,
                postings=postings
            )
        return None


class TravelBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        if self.txn.payee_name.startswith(('TRV', 'TRB', 'TRT')):
            return self._make_transaction(
                self.txn.date,
                payee=self.memo_parser.extract_payee(),
                narration=self.memo_parser.extract_narration(),
                tags=set([travel_name_to_tag(self.txn.payee_name), 'trip']).union(
                    self.memo_parser.extract_tags()
                ),
                postings=self._make_postings()
            )
        return None


class ExpenseBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        return None


DEFAULT_BEANIFIERS = [
    InflowBeanifier,
    TransferBeanifier,
    TravelBeanifier
]


def print_ytxn(t: YTransaction):
    print(t.date, t.account_name, t.payee_name, t.memo, t.category_name, t.amount, sep='|')
    for s in t.subtransactions:
        print("  ", s.payee_name, s.memo, s.category_name, s.amount, sep='|')


def beanify(
        transactions: List[YTransaction],
        beanifiers: List[YNABBeanifier]=DEFAULT_BEANIFIERS,
        ) -> List[NamedTuple]:
    getcontext().prec = 60
    beancount_transactions = []
    handled_transfers = []
    for t in transactions:
        if t.id not in handled_transfers:
            if t.transfer_transaction_id:
                handled_transfers.append(t.transfer_transaction_id)
            try:
                for b in beanifiers:
                    btxn = b(t).beanify()
                    if btxn:
                        beancount_transactions.append(btxn)
                        break
            except Exception as ex:
                print_ytxn(t)
                raise ex
    return beancount_transactions

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
from src.modules.ynab.beancount.mappers import AccountMapper, CategoryMapper

from .mapping.payees import map_inflow
from .parsing.utils import travel_name_to_tag
from .parsing.memo_parsers import memo_parser


class YNABBeanifier(ABC):

    def __init__(self, transaction: YTransaction):
        self.txn = transaction
        self.converters: List[YNABtoPostingConverter] = [
            StartingBalanceConverter,
            InflowConverter,
            TransferConverter,
            ExpenseConverter,
        ]
        self.memo_parser = memo_parser(self.txn.memo)

    @abstractmethod
    def beanify(self) -> NamedTuple:
        raise NotImplementedError()

    @staticmethod
    def is_investment(transaction: YTransaction):
        return (transaction.account_name == 'Investments'
            or transaction.payee_name == 'Transfer : Investments'
            or transaction.payee_name in ('Coupon', 'Dividends')
            or (transaction.memo and transaction.memo.startswith('ACCRUAL')))

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
                    break
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


class StartingBalanceBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        if self.txn.payee_name == 'Starting Balance':
            return self._make_transaction(
                self.txn.date,
                self.txn.payee_name.strip(),
                narration=self.txn.memo,
                postings=self._make_postings()
            )
        return None


class InflowBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        if ((self.txn.payee_name == 'Paycheck'
             or self.txn.category_name == 'Inflow: Ready to Assign')
            and self.txn.transfer_account_id is None
            and not self.is_investment(self.txn)):
            return self._make_transaction(
                self.txn.date,
                self.txn.payee_name.strip(),
                narration=self.txn.memo,
                postings=self._make_postings()
            )
        return None


class InvestmentBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        if self.is_investment(self.txn):
            return self._make_transaction(
                self.txn.date,
                self.txn.payee_name.strip(),
                narration=self.txn.memo,
                postings=self._make_postings()
            )
        return None


class TransferBeanifier(YNABBeanifier):

    def beanify(self) -> NamedTuple:
        if (self.txn.transfer_transaction_id is not None
            and not self.is_investment(self.txn)):
            payee = self.memo_parser.extract_payee()
            tags = self.memo_parser.extract_tags()
            postings = self._make_postings()
            is_payment = any([p.account.startswith('Liabilities') and p.units.number > 0 for p in postings])
            is_borrowing = any([p.account.startswith('Liabilities') and p.units.number < 0 for p in postings])
            is_payback = all(
                    [p.account.startswith('Assets') for p in postings]
                ) and any(
                    [p.account.startswith('Assets:Lending') and p.units.number < 0 for p in postings]
                )
            if not payee:
                if is_payment:
                    payee = 'Debt Payment'
                elif is_borrowing:
                    payee = 'Borrowing'
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
        if (self.txn.category_name is not None
            and self.txn.category_name != 'Uncategorized'):
            return self._make_transaction(
                self.txn.date,
                payee=self.txn.payee_name,
                narration=self.memo_parser.extract_narration(),
                tags=self.memo_parser.extract_tags(),
                postings=self._make_postings()
            )
        return None


DEFAULT_BEANIFIERS = [
    StartingBalanceBeanifier,
    InflowBeanifier,
    TransferBeanifier,
    TravelBeanifier,
    ExpenseBeanifier
]


def beanify(
        transactions: List[YTransaction],
        beanifiers: List[YNABBeanifier]=DEFAULT_BEANIFIERS,
        ) -> List[NamedTuple]:
    getcontext().prec = 60
    beancount_transactions = []
    handled_transfers = []
    handled_transactions = []
    for t in transactions:
        if t.id not in handled_transfers:
            handled = False
            try:
                for b in beanifiers:
                    btxn = b(t).beanify()
                    if btxn:
                        handled = True
                        beancount_transactions.append(btxn)
                        break
            except Exception as ex:
                print(t.describe())
                raise ex
            if handled:
                handled_transactions.append(t.id)
                for subt in (t.subtransactions if t.subtransactions + [t] else [t]):
                    if subt.transfer_transaction_id:
                        handled_transfers.append(subt.transfer_transaction_id)
    for t in transactions:
        if t.id not in handled_transactions and t.id not in handled_transfers:
            print(t.describe())
    return beancount_transactions

import datetime
import re
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
from functools import cmp_to_key
from typing import Dict, List, NamedTuple, Set

from beancount import loader
from beancount.core.amount import add as add_amounts
from beancount.core.amount import sub as sub_amounts
from beancount.core.data import Amount, Meta
from beancount.core.data import Posting as BPosting
from beancount.core.data import Transaction as BTransaction

from src.modules.ynab.api.models.transactions import \
    Subtransaction as YSubtransaction
from src.modules.ynab.api.models.transactions import \
    Transaction as YTransaction
from src.modules.ynab.beancount.mappers import (AccountMapper,
                                                        CategoryMapper)

from .mapping.payees import map_inflow
from .parsing.memo_parsers import memo_parser
from .parsing.utils import travel_name_to_tag


class YNABtoPostingConverter(ABC):

    def __init__(self, transaction: YTransaction | YSubtransaction) -> None:
        self.txn = transaction
        self.memo_parser = memo_parser(self.txn.memo)
        self.account_mapper: AccountMapper = AccountMapper()
        self.category_mapper: CategoryMapper = CategoryMapper()

    @abstractmethod
    def convert(self) -> List[BPosting]:
        raise NotImplementedError()

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


class StartingBalanceConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if (self.txn.payee_name == 'Starting Balance'):
            a_from = 'Equity:OpeningBalance'
            a_to = self.account_mapper.map(self.txn.account_name)
            return [
                self._make_posting(a_from, -self.txn.amount),
                self._make_posting(a_to, self.txn.amount)
            ]
        return None


class InflowConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if (self.txn.category_name == 'Inflow: Ready to Assign'
            and self.txn.payee_name != 'Starting Balance'
            and not self.txn.transfer_account_id
            and not YNABBeanifier.is_investment(self.txn)):
            a_from, a_to = map_inflow(self.txn.payee_name)(self.txn)
            a_from = self.account_mapper.map(a_from)
            a_to = self.account_mapper.map(a_to)
            return [
                self._make_posting(a_from, -self.txn.amount),
                self._make_posting(a_to, self.txn.amount)
            ]
        return None


class TransferConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if (self.txn.transfer_transaction_id is not None
            and self.txn.payee_name != 'Starting Balance'
            and not YNABBeanifier.is_investment(self.txn)):
            a_from = [self.account_mapper.map(self.txn.account_name)]
            a_to = [self.account_mapper.map(self.txn.payee_name.split(':')[1].strip())]
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


class ExpenseConverter(YNABtoPostingConverter):

    def convert(self) -> List[BPosting]:
        if (self.txn.category_name != 'Inflow: Ready to Assign'
            and self.txn.payee_name != 'Starting Balance'
            and not self.txn.transfer_account_id
            and not YNABBeanifier.is_investment(self.txn)
            and self.txn.amount < 0):
            return [
                self._make_posting(self.account_mapper.map(self.txn.account_name), self.txn.amount),
                self._make_posting(
                    self.category_mapper.map(self.txn.category_name)
                    + f':{self.txn.payee_name.title().replace(" ", "")}',
                    -self.txn.amount
                )
            ]
        return None

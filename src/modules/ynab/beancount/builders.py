import datetime
from decimal import Decimal
from functools import cmp_to_key
from typing import List, NamedTuple, Set

from beancount.core.data import Amount, Flag, Meta, Posting
from beancount.core.position import Cost, CostSpec

from src.modules.ynab.beancount.utils.beancount import BeancountTransaction
from src.modules.ynab.beancount.utils.numbers import to_decimal
from src.modules.ynab.beancount.utils.postings import cmp, combine


class _Posting:

    def __init__(self):
        self._account: str = None
        self._units: Amount = None
        self._cost: Cost | CostSpec = None
        self._price: Amount = None
        self._flag: Flag = None
        self._meta: Meta = {}

    def to_posting(self) -> Posting:
        return Posting(
            self._account,
            self._units,
            self._cost,
            self._price,
            self._flag,
            self._meta
        )


class BeanPostingBuilder:

    def __init__(self):
        self.__pst: _Posting = _Posting()

    def set_account(self, account: str) -> "BeanPostingBuilder":
        assert account is not None
        self.__pst._account = account
        return self

    def set_units(self, amount: int, currency: str='EUR', precision=2) -> "BeanPostingBuilder":
        assert amount is not None
        self.__pst._units = Amount(
            to_decimal(amount, precision),
            currency
        )
        return self

    def set_cost(
            self,
            date: datetime.date|str=None,
            cost: int=None,
            currency: str=None,
            precision=2,
    ) -> "BeanPostingBuilder":
        assert date is not None
        assert cost is not None
        self.__pst._cost = Cost(
            to_decimal(cost, precision),
            currency,
            date,
            None
        )
        return self

    def set_costspec(
            self,
            date: datetime.date=None,
            cost: int=None,
            currency: str=None,
            merge=True,
            precision=2,
    ) -> "BeanPostingBuilder":
        self.__pst._cost = CostSpec(
            to_decimal(cost, precision) if cost else None,
            None,
            currency,
            date,
            None,
            merge
        )
        return self

    def set_price(self, price: int, currency: str='EUR', precision=2) -> "BeanPostingBuilder":
        assert price is not None
        self.__pst._price = Amount(
            to_decimal(price, precision),
            currency
        )
        return self

    def set_meta(self, meta: Meta) -> "BeanPostingBuilder":
        self.__pst._meta = meta if meta else {}
        return self

    def build(self, clear=True) -> NamedTuple:
        product = self.__pst.to_posting()
        if clear:
            self.__pst = _Posting()
        return product


class BeanTransactionBuilder:

    def __init__(self):
        self.__txn = BeancountTransaction()

    def set_date(self, date: datetime.date) -> "BeanTransactionBuilder":
        assert date is not None
        self.__txn.date = date
        return self

    def set_payee(self, payee: str) -> "BeanTransactionBuilder":
        assert payee is not None
        self.__txn.payee = payee.strip() if payee else None
        return self

    def set_narration(self, narration: str) -> "BeanTransactionBuilder":
        self.__txn.narration = narration.strip() if narration else None
        return self

    def set_tags(self, tags: Set[str]) -> "BeanTransactionBuilder":
        self.__txn.tags = tags
        return self

    def set_meta(self, meta: Meta) -> "BeanTransactionBuilder":
        self.__txn.meta = meta
        return self

    def set_postings(self, postings: List[Posting]) -> "BeanTransactionBuilder":
        if not postings:
            postings = []
        self.__txn.postings = postings
        return self

    def add_posting(self, posting: Posting, merge=True) -> "BeanTransactionBuilder":
        assert posting is not None
        postings = self.__txn.postings
        added = False
        if merge:
            for i in range(len(postings)):
                combined = combine(postings[i], posting)
                if combined:
                    postings[i] = combined
                    added = True
                    break
        if not added:
            postings.append(posting)
        self.__txn.postings = sorted(postings, key=cmp_to_key(cmp))
        return self

    def current_postings(self) -> List[Posting]:
        return self.__txn.postings

    def build(self, clear=True) -> BeancountTransaction:
        product = self.__txn
        if clear:
            self.__txn = BeancountTransaction()
        return product

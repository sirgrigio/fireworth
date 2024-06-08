import datetime
from decimal import Decimal
from functools import cmp_to_key
from typing import List, NamedTuple, Set, Union

from beancount.core.data import (Account, Amount, Cost, CostSpec, Flag, Meta,
                                 Posting, Transaction)

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
            Decimal(amount/1000).quantize(Decimal(10)**-precision),
            currency
        )
        return self

    def set_cost(self, cost) -> "BeanPostingBuilder":
        assert cost is not None
        self.__pst._cost = cost
        return self

    def set_price(self, price: int, currency: str='EUR', precision=2) -> "BeanPostingBuilder":
        assert price is not None
        self.__pst._units = Amount(
            Decimal(price/1000).quantize(Decimal(10)**-precision),
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


class _Transaction:

    def __init__(self):
        self._date: datetime.date = None
        self._payee: str = None
        self._flag: str = '*'
        self._narration: str = None
        self._tags: Set[str] = []
        self._meta: Meta = {}
        self._links: Set[str] = []
        self._postings: List[Posting] = []

    def to_transaction(self) -> NamedTuple:
        return Transaction(
            self._meta,
            self._date,
            self._flag,
            self._payee,
            self._narration,
            self._tags,
            self._links,
            self._postings
        )


class BeanTransactionBuilder:

    def __init__(self):
        self.__txn: _Transaction = _Transaction()

    def set_date(self, date: datetime.date) -> "BeanTransactionBuilder":
        assert date is not None
        self.__txn._date = date
        return self

    def set_payee(self, payee: str) -> "BeanTransactionBuilder":
        assert payee is not None
        self.__txn._payee = payee.strip() if payee else None
        return self

    def set_narration(self, narration: str) -> "BeanTransactionBuilder":
        self.__txn._narration = narration.strip() if narration else None
        return self

    def set_tags(self, tags: Set[str]) -> "BeanTransactionBuilder":
        self.__txn._tags = tags
        return self

    def set_meta(self, meta: Meta) -> "BeanTransactionBuilder":
        self.__txn._meta = meta
        return self

    def set_postings(self, postings: List[Posting]) -> "BeanTransactionBuilder":
        if not postings:
            postings = []
        self.__txn._postings = postings
        return self

    def add_posting(self, posting: Posting, merge=True) -> "BeanTransactionBuilder":
        assert posting is not None
        postings = self.__txn._postings
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
        self.__txn._postings = sorted(postings, key=cmp_to_key(cmp))
        return self

    def current_postings(self) -> List[Posting]:
        return self.__txn._postings

    def build(self, clear=True) -> NamedTuple:
        product = self.__txn.to_transaction()
        if clear:
            self.__txn = _Transaction()
        return product

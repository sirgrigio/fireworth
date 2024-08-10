import datetime
from typing import Any, List, NamedTuple, Set
from beancount.core.data import Meta, Posting, Transaction


class BeancountTransaction:

    def __init__(
            self,
            date: datetime.date=None,
            payee: str=None,
            flag: str='*',
            narration: str=None,
            tags: Set[str]=None,
            meta: Meta=None,
            links: Set[str]=None,
            postings: List[Posting]=None
        ):
        self.date: datetime.date = date
        self.payee: str = payee
        self.flag: str = flag
        self.narration: str = narration
        self.tags: Set[str] = [_ for _ in tags] if tags else []
        self.meta: Meta = {k: v for k,v in meta.items()} if meta else {}
        self.links: Set[str] = [_ for _ in links] if links else []
        self.postings: List[Posting] = [_ for _ in postings] if postings else []

    def to_transaction(self) -> NamedTuple:
        return Transaction(
            self.meta,
            self.date,
            self.flag,
            self.payee,
            self.narration,
            self.tags,
            self.links,
            self.postings
        )

    def __repr__(self) -> str:
        return f'BeancountTransaction[date={self.date}; payee="{self.payee}"; narration="{self.narration}"]'

    @staticmethod
    def from_dict(obj: Any) -> "BeancountTransaction":
        assert isinstance(obj, dict)
        return BeancountTransaction(
            date=obj.get('date', None),
            payee=obj.get('payee', None),
            flag=obj.get('flag', None),
            narration=obj.get('narration', None),
            tags=obj.get('tags', None),
            meta=obj.get('meta', None),
            links=obj.get('links', None),
            postings=obj.get('postings', [])
        )

from beancount.core.amount import add
from beancount.core.data import Posting


def cmp(p1: Posting, p2: Posting) -> int:
    if (p1.units.number.is_signed() != p2.units.number.is_signed()
        or p1.account == p2.account):
        return p1.units.number - p2.units.number
    else:
        return -1 if p1.account <= p2.account else 1


def combine(p1: Posting, p2: Posting) -> Posting:
    if (
        p1.account == p2.account
        and p1.units.currency == p2.units.currency
        and p1.cost == p2.cost
        and p1.price == p2.price
        and p1.flag == p2.flag
        and all([k in p2.meta and v == p2.meta[k] for k,v in p1.meta.items()])
        and all([k in p1.meta and v == p1.meta[k] for k,v in p2.meta.items()])
    ):
        return Posting(
            p1.account,
            add(p1.units, p2.units),
            p1.cost,
            p1.price,
            p1.flag,
            {k: v for k,v in p1.meta.items()}
        )
    else:
        return None

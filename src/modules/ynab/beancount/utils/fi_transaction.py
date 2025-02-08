from abc import ABC

from src.modules.ynab.beancount.utils.numbers import to_int_or_float


class XRateWrapper:

    def __init__(self, currency_a: str, currency_b: str, rate_ab: float):
        self.currency_a = currency_a
        self.currency_b = currency_b
        self.rate_ab = rate_ab

    def convert(self, currency, amount) -> float:
        if currency == self.currency_a:
            return amount * self.rate_ab
        elif currency == self.currency_b:
            return amount / self.rate_ab
        else:
            raise ValueError(currency)

    def rate(self, currency) -> float:
        if currency == self.currency_a:
            return self.rate_ab
        elif currency == self.currency_b:
            return 1 / self.rate_ab
        else:
            raise ValueError(currency)

    def other(self, currency) -> str:
        if currency == self.currency_a:
            return self.currency_b
        elif currency == self.currency_b:
            return self.currency_a
        else:
            raise ValueError(currency)


class FITransaction(ABC):

    def __init__(
            self,
            symbol: str=None,
            src_acc: str=None,
            dst_acc: str=None,
            currency: str=None,
            quantity: str=None,
            unit_price: str=None,
            xcurr_a: str=None,
            xcurr_b: str=None,
            xrate_ab: str=None,
            xqt: str=None,
    ):
        self._symbol = symbol
        self._src_acc = src_acc
        self._dst_acc = dst_acc
        self._currency = currency
        self._quantity = to_int_or_float(quantity) if quantity is not None else None
        self._unit_price = float(unit_price) if unit_price is not None else None
        self._xcurr_a = str(xcurr_a) if xcurr_a is not None else None
        self._xcurr_b = str(xcurr_b) if xcurr_b is not None else None
        self._xrate_ab = float(xrate_ab) if xrate_ab is not None else None
        self._xqt = float(xqt) if xqt is not None else None
        if self._xcurr_a and self._xcurr_b and self._xrate_ab:
            self._xratewrapper = XRateWrapper(self._xcurr_a, self._xcurr_b, self._xrate_ab)
        else:
            self._xratewrapper = None

    @staticmethod
    def factory(type: str=None, **kwargs) -> "FITransaction":
        if type == "STARTING_BALANCE":
            return StartingBalanceTransaction(**kwargs)
        elif type == "BUY":
            return BuyTransaction(**kwargs)
        elif type == "SELL":
            return SellTransaction(**kwargs)
        elif type == "MATURITY":
            return MaturityTransaction(**kwargs)
        elif type == "EXCHANGE":
            return ExchangeTransaction(**kwargs)
        elif type == "DIVIDENDS":
            return DividendsTransaction(**kwargs)
        elif type == "COUPON":
            return CouponTransaction(**kwargs)
        elif type == "ACCRUAL":
            return AccrualTransaction(**kwargs)
        else:
            raise ValueError(f"Invalid transaction type: {type}")

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def src_acc(self) -> str:
        return self._src_acc

    @property
    def dst_acc(self) -> str:
        return self._dst_acc

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def quantity(self) -> int | float:
        return self._quantity

    @property
    def unit_price(self) -> float:
        return self._unit_price

    @property
    def xcurr_a(self) -> str:
        return self._xcurr_a

    @property
    def xcurr_b(self) -> str:
        return self._xcurr_b

    @property
    def xrate_ab(self) -> float:
        return self._xrate_ab

    @property
    def xqt(self) -> float:
        return self._xqt


class StartingBalanceTransaction(FITransaction):
    pass


class BuyTransaction(FITransaction):
    pass


class SellTransaction(FITransaction):

    @property
    def quantity(self) -> int | float:
        return -self._quantity


class MaturityTransaction(FITransaction):

    @property
    def quantity(self) -> int | float:
        return -self._quantity


class ExchangeTransaction(FITransaction):

    @property
    def symbol(self) -> str:
        return self._xratewrapper.other(self._currency or self.xcurr_b)

    @property
    def src_acc(self) -> str:
        return self._src_acc

    @property
    def dst_acc(self) -> str:
        return self._dst_acc

    @property
    def currency(self) -> str:
        return self._currency or self._xcurr_a

    @property
    def quantity(self) -> float:
        return self._xqt

    @property
    def unit_price(self) -> float:
        return round(self._xratewrapper.rate(self.symbol), 4)

    @property
    def xcurr_a(self) -> str:
        return self._xcurr_a

    @property
    def xcurr_b(self) -> str:
        return self._xcurr_b

    @property
    def xrate_ab(self) -> float:
        return self._xrate_ab

    @property
    def xqt(self) -> float:
        return self._xqt


class DividendsTransaction(FITransaction):
    pass


class CouponTransaction(FITransaction):
    pass


class AccrualTransaction(FITransaction):
    pass

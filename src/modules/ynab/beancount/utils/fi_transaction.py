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
        if type == "BUY":
            return BuyTransaction(**kwargs)
        elif type == "SELL":
            return SellTransaction(**kwargs)
        elif type == "MATURITY":
            return MaturityTransaction(**kwargs)
        elif type == "EXCHANGE":
            return ExchangeTransaction(**kwargs)
        elif type == "ACCRUAL" or type == "COUPON" or type == "DIVIDENDS":
            return DividendTransaction(**kwargs)
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


class BuyTransaction(FITransaction):

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
        super().__init__(
            symbol=symbol,
            src_acc=src_acc,
            dst_acc=dst_acc,
            currency=currency,
            quantity=quantity,
            unit_price=unit_price,
            xcurr_a=xcurr_a,
            xcurr_b=xcurr_b,
            xrate_ab=xrate_ab,
            xqt=xqt,
        )


class SellTransaction(FITransaction):

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
        super().__init__(
            symbol=symbol,
            src_acc=src_acc,
            dst_acc=dst_acc,
            currency=currency,
            quantity=quantity,
            unit_price=unit_price,
            xcurr_a=xcurr_a,
            xcurr_b=xcurr_b,
            xrate_ab=xrate_ab,
            xqt=xqt,
        )

    @property
    def quantity(self) -> int | float:
        return -self._quantity


class MaturityTransaction(FITransaction):

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
        super().__init__(
            symbol=symbol,
            src_acc=src_acc,
            dst_acc=dst_acc,
            currency=currency,
            quantity=quantity,
            unit_price=unit_price,
            xcurr_a=xcurr_a,
            xcurr_b=xcurr_b,
            xrate_ab=xrate_ab,
            xqt=xqt,
        )

    @property
    def quantity(self) -> int | float:
        return -self._quantity


class ExchangeTransaction(FITransaction):

    def __init__(
            self,
            src_acc: str=None,
            dst_acc: str=None,
            currency: str=None,
            xcurr_a: str=None,
            xcurr_b: str=None,
            xrate_ab: str=None,
            xqt: str=None,
    ):
        super().__init__(
            src_acc=src_acc,
            dst_acc=dst_acc,
            currency=currency,
            xcurr_a=xcurr_a,
            xcurr_b=xcurr_b,
            xrate_ab=xrate_ab,
            xqt=xqt
        )

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


class DividendTransaction(FITransaction):
    pass

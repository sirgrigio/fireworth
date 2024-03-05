import math
import re

from src.utils.xrate import XRate

_TRADE_REGEX = '(?P<type>(BUY|SELL|MATURITY))(\[(?P<currency>[A-Z]+)\])?: ' +\
                '(?P<symbol>[A-Z0-9\.]+) (?P<quantity>[0-9\.]+)@(?P<unit_price>[0-9\.]+)' +\
                '( (?P<xcurra>[A-Z]+)-(?P<xcurrb>[A-Z]+) 1:(?P<xrateab>[0-9\.]+))?' +\
                '( \[ACCSRC:(?P<accsrc>.+)\])?( \[ACCDST:(?P<accdst>.+)\])?'

_EXCHANGE_REGEX = '(?P<type>EXCHANGE)(\[(?P<currency>[A-Z]+)\])?: ' +\
                    '(?P<xcurra>[A-Z]+)-(?P<xcurrb>[A-Z]+) 1:(?P<xrateab>[0-9\.]+) (?P<xqt>[0-9\.]+)' +\
                    '( \[ACCSRC:(?P<accsrc>.+)\])?( \[ACCDST:(?P<accdst>.+)\])?'

_INTEREST_REGEX = '(?P<type>(ACCRUAL|COUPON|DIVIDENDS))(\[(?P<currency>[A-Z]+)\])?: (?P<symbol>[A-Z0-9\.]+)' +\
                    '( \[ACCSRC:(?P<accsrc>.+)\])?( \[ACCDST:(?P<accdst>.+)\])?'

_REGEX_LOOKUP = {
    'BUY': _TRADE_REGEX,
    'SEL': _TRADE_REGEX,
    'MAT': _TRADE_REGEX,
    'EXC': _EXCHANGE_REGEX,
    'ACC': _INTEREST_REGEX,
    'COU': _INTEREST_REGEX,
    'DIV': _INTEREST_REGEX,
}


class YNABMemoInfo:

    def __init__(
            self,
            optype,
            accsrc,
            accdst,
            currency,
            symbol,
            quantity,
            unit_price,
            amount,
    ):
        self.optype: str = optype
        self.accsrc: str = accsrc
        self.accdst: str = accdst
        self.currency: str = currency
        self.symbol: str = symbol
        self.quantity: float = quantity
        self.unit_price: float = unit_price
        self.amount: float = amount


def parse_memo(memo: str, amount: float, refcurr: str='EUR') -> YNABMemoInfo:
    if memo[:3] not in _REGEX_LOOKUP:
        return None
    match = re.search(_REGEX_LOOKUP[memo[:3]], memo)
    if not match:
        raise ValueError(f'memo not matching known patterns: {memo}')
    optype = match.group('type')
    accsrc = match.group('accsrc')
    accdst = match.group('accdst')
    currency = match.group('currency')
    currency = currency if currency else refcurr
    if optype == 'BUY' or optype == 'SELL' or optype == 'MATURITY':
        symbol = match.group('symbol')
        quantity = math.copysign(float(match.group('quantity')), amount)
        unit_price = float(match.group('unit_price'))
    elif optype == 'EXCHANGE':
        xrate = XRate(match.group('xcurra'), match.group('xcurrb'), float(match.group('xrateab')))
        symbol = xrate.other(currency)
        quantity = math.copysign(float(match.group('xqt')), amount)
        unit_price = float(xrate.rate(symbol))
    elif optype == 'ACCRUAL' or optype == 'COUPON' or optype == 'DIVIDENDS':
        symbol = match.group('symbol')
        quantity = None
        unit_price = None
    else:
        raise NotImplementedError(optype)
    amount = quantity * unit_price if currency != refcurr else amount
    return YNABMemoInfo(
        optype,
        accsrc,
        accdst,
        currency,
        symbol,
        quantity,
        unit_price,
        amount
    )

import csv
import logging
from typing import List

import pandas as pd

import src.utils.ynab.transaction as ynabt

_logger = logging.getLogger(__name__)


class Ledger:

    def __init__(
            self,
            refcurrency: str='EUR',

    ):
        self._df = None
        self.refcurrency = refcurrency

    def init(self, df: pd.DataFrame):
        self._df = df.copy(deep=True)
        return self

    def accounts(self) -> List[str]:
        return self._df.account.unique().tolist()

    def account_history(self, account, start=None, end=None, currency=None):
        dfa = self._df.loc[self._df['account'] == account]
        is_symbol = dfa['is_symbol'].all()
        if is_symbol:
            return dfa[['account', 'target_account', 'payee', 'memo', 'quantity']]
        else:
            return dfa[['account', 'target_account', 'payee', 'memo', 'amount', 'currency']]


    def balance(self, freq='M', start=None, end=None):
        res = self._df.copy(deep=True)
        if end: res = res[res.date <= end]
        res['value'] = res.apply(lambda x: x.amount if not x.is_symbol else x.quantity, axis=1)
        period_range = pd.period_range(min(res.date), end, freq=freq, name='date')
        res = (
            res.groupby(['account', pd.PeriodIndex(res.date, freq=freq)])['value'].sum()
                .groupby(level=[0]).cumsum()
                .unstack('account')
                .ffill()
                .reindex(period_range, method='ffill')
                .stack('account')
                .reset_index(name='balance')
        )
        if start: res = res[res.apply(lambda x: x.date.to_timestamp().date() >= start, axis=1)]
        res.balance = round(res.balance, 2)
        res = res.pivot(index='account', columns='date', values='balance')
        return res.loc[(res != 0).any(axis=1)]


def from_ynab_register(filename, currency='EUR'):
    result = []
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            try:
                t = ynabt.from_csv(*row)
                if t.payee != 'Profit & Loss':
                    result.append(t.to_ledger(currency))
            except Exception as ex:
                _logger.warning(f'unable to parse row: {row}')
                _logger.exception(ex)
    return Ledger().init(df=pd.DataFrame(result))

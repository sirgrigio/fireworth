import logging
from typing import Dict, List

from src.modules.ynab.api.models.transactions import (Subtransaction,
                                                      Transaction)
from src.modules.ynab.beancount.parsers import \
    FinancialInstrumentTransactionParser
from src.modules.ynab.beancount.utils.strings import camelcased

log = logging.getLogger(__name__)


class MappingHelper:

    def __init__(self, transactions: List[Transaction]):
        self.__txns = transactions

    def __suggest_mapping(self, prefix: str='', tokens: List[str]=[]) -> str:
        return ':'.join([prefix] + [''.join(camelcased(t)) for t in tokens])

    def accounts(self) -> Dict[str, str]:
        accounts = {}
        for t in self.__txns:
            for _ in [t] + t.subtransactions:
                accounts.update({_.account_name: ''})
        return accounts

    def inflows(self) -> Dict[str, Dict[str, str]]:
        def __inflow(t: Transaction | Subtransaction) -> Dict[str, Dict[str, str]]:
            if t.amount > 0 and not t.transfer_account_id and t.category_name != 'Split':
                if t.category_name in ('Inflow: Ready to Assign', 'Uncategorized'):
                    return {t.payee_name: ''}
                else:
                    log.warning(f'check inflow transaction with category "{t.category_name}": {t.describe(sep="|--")}')
            return {}
        inflows = {}
        for t in self.__txns:
            for _ in [t] + t.subtransactions:
                inflows.update(__inflow(_))
        return inflows

    def expenses(self, expand_all=False) -> Dict[str, Dict[str, str]]:
        expenses = {}
        categories_to_expand = []
        for t in self.__txns:
            for e in [t] + t.subtransactions:
                if (e.transfer_account_id is not None
                    or e.category_name in ('Inflow: Ready to Assign', 'Split', 'Uncategorized')):
                    continue
                if (e.category_name not in categories_to_expand
                    and e.payee_name != t.payee_name):
                    categories_to_expand.append(e.category_name)
                if e.category_name not in expenses:
                    expenses[e.category_name] = {'.': self.__suggest_mapping('Expenses', [e.category_name])}
                if not e.payee_name in expenses[e.category_name]:
                    expenses[e.category_name].update({
                        e.payee_name: self.__suggest_mapping(
                            'Expenses',
                            [e.category_name, e.payee_name]
                        )
                    })
        for c in expenses:
            if not c in categories_to_expand and not expand_all:
                expenses[c] = {'.': expenses[c]['.']}
        return expenses


    def investment_accounts(self, parsers: List[FinancialInstrumentTransactionParser]) -> Dict[str, str]:
        accounts = {}
        for t in self.__txns:
            if t.payee_name == 'Transfer : Investments':
                for parser in parsers:
                    fitxn = parser.parse(t)
                    if fitxn:
                        accounts.update({fitxn.src_acc: ''})
                        accounts.update({fitxn.dst_acc: ''})
                        accounts.update({fitxn.symbol: ''})
                        accounts.update({fitxn.xcurr_a: ''})
                        accounts.update({fitxn.xcurr_b: ''})
        return accounts

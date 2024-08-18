
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
from collections import defaultdict

import yaml
import re

from src.modules.ynab.api.models.transactions import (Subtransaction,
                                                      Transaction)
from src.modules.ynab.beancount.utils.conditions import StrFieldCondition

log = logging.getLogger(__name__)


class _TransactionSelector:

    def __init__(self, main_transaction=False, conditions: Dict[str, str]={}):
        self.__main = main_transaction
        self.__condition = [
            StrFieldCondition(f, p)
            for f, p in conditions.items()
        ]

    @property
    def is_main(self):
        return self.__main

    def match(self, transaction: Transaction) -> bool:
        return all([c.match(transaction) for c in self.__condition])


class Merger:

    def __init__(
            self,
            fields: List[str],
            selectors: List[Dict[str, str]]=[]
            ):
        self.log = logging.getLogger(self.__class__.__name__)
        assert fields is not None
        assert len(fields) > 0
        assert selectors is not None
        assert len(selectors) > 1
        self.__fields = fields
        self.__selectors: List[_TransactionSelector] = [
            _TransactionSelector(
                main_transaction=selector.get('main_transaction', False),
                conditions=selector.get('conditions', [])
            ) for selector in selectors
        ]

    def __repr__(self) -> str:
        return f'Merger({self.__selectors} BY {self.__fields})'


    def merge(self, transactions: List[Transaction]) -> List[Transaction]:
        merged_ids = set()
        grouped_transactions: Dict[Transaction, List[Transaction]] = defaultdict(list)
        for txn in transactions:
            if any([s.match(txn) for s in self.__selectors]):
                log.debug(f'{self} selecting transaction to be merged: {txn.describe(sep=" >> ")}')
                grouped_transactions[tuple([getattr(txn, f) for f in self.__fields])].append(txn)

        merged_transactions = []
        for _, txn_group in grouped_transactions.items():
            log.debug(f'{self} trying to merge group {_} of size {len(txn_group)}')
            if not all([any([s.match(t) for t in txn_group]) for s in self.__selectors]):
                log.debug(f'group {_} does not contains enough transactions - no merging')
                merged_transactions.extend(txn_group)
            else:
                main_txn = next(t for t in txn_group if any([s.match(t) and s.is_main for s in self.__selectors]))
                merged_subtransactions = []
                for i, txn in enumerate(txn_group):
                    log.debug(f'group {_}/{i}: {txn.describe(sep=" >> ")}')
                    merged_ids.add(txn.id)
                    merged_subtransactions.extend(txn.subtransactions)
                    if not txn.subtransactions:
                        subtxn_dict = {k:v for k,v in txn.__dict__.items()}
                        subtxn_dict['id'] = f'sub_{txn.id}'
                        subtxn_dict['transaction_id'] = main_txn.id
                        merged_subtransactions.append(Subtransaction.from_dict(subtxn_dict))
                merged_txn = Transaction.from_dict(main_txn.__dict__)
                merged_txn.amount = sum(txn.amount for txn in txn_group)
                merged_txn.subtransactions = merged_subtransactions
                log.info(f'{self} new merged transaction: {merged_txn.describe(sep=" >> ")}')
                merged_transactions.append(merged_txn)

        final_transactions = []
        added_merged = set()
        for txn in transactions:
            if txn.id in merged_ids and txn.id not in added_merged:
                for merged_txn in merged_transactions:
                    if merged_txn.id == txn.id:
                        final_transactions.append(merged_txn)
                        added_merged.add(merged_txn.id)
                        break
            else:
                final_transactions.append(txn)
        return final_transactions

    @staticmethod
    def apply(mergers: List["Merger"], obj_list: List[Transaction]) -> Any:
        new_list = obj_list
        for m in mergers:
            new_list = m.merge(new_list)
        return new_list


def from_yml_file(filename: Path | str, node: List[str]=['mergers']) -> List[Merger]:
    assert filename is not None
    if type(filename) == str:
        filename = Path(filename)
    assert filename.exists()
    mergers: List[Merger] = []
    with open(filename, 'r') as f:
        yamlconf = yaml.safe_load(f)
        for n in node:
            yamlconf = yamlconf.get(n)
        for item in yamlconf:
            merger = Merger(
                fields=item['fields'],
                selectors=item.get('selectors', [])
            )
            if merger:
                mergers.append(merger)
                log.info(f'loaded merger {merger}')
    return mergers

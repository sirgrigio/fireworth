
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import yaml
import re

from src.modules.ynab.api.models.transactions import (Subtransaction,
                                                      Transaction)
from src.modules.ynab.beancount.utils.conditions import StrFieldCondition

log = logging.getLogger(__name__)


class Merger:

    def __init__(self, fields: List[str], conditions: Dict[str, str]={}):
        self.log = logging.getLogger(self.__class__.__name__)
        assert fields is not None
        assert len(fields) > 0
        self.__fields = fields
        self.__conditions: List[StrFieldCondition] = [
            StrFieldCondition(f, p) for f, p in conditions.items()
        ] if conditions else []

    def merge(self, transactions: List[Transaction]) -> List[Transaction]:
        result = []
        merged = []
        for t in transactions:
            if all([c.match(t) for c in self.__conditions]):
                for m in merged:
                    pass
            result.append(t)
        return result


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
                conditions=item.get('conditions', {})
            )
            if merger:
                mergers.append(merger)
                log.info(f'loaded merger {merger}')
    return mergers

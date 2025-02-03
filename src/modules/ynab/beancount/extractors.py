
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.modules.ynab.api.models.transactions import (Subtransaction,
                                                      Transaction)
from src.modules.ynab.beancount.utils.conditions import StrFieldCondition

log = logging.getLogger(__name__)


class Extractor(ABC):

    def __init__(self, field: str, conditions: Dict[str, str]={}, remove_after=True):
        self.log = logging.getLogger(self.__class__.__name__)
        assert field is not None
        self.__field = field
        self.__conditions: List[StrFieldCondition] = [
            StrFieldCondition(f, p) for f, p in conditions.items()
        ] if conditions else []
        self.__remove_after = remove_after

    @property
    def _field(self):
        return self.__field

    @property
    def _conditions(self):
        return self.__conditions

    @abstractmethod
    def _extract(self, transaction: Transaction | Subtransaction) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def _remove_after(self, transaction: Transaction | Subtransaction) -> Any:
        raise NotImplementedError()

    def extract(self, transaction: Transaction | Subtransaction, default=None) -> Any:
        if all([c.match(transaction) for c in self._conditions]):
            result = self._extract(transaction)
            if result and self.__remove_after:
                self._remove_after(transaction)
            return result
        return default


class SimpleExtractor(Extractor):

    def __init__(self, field: str, pattern: str, conditions: Dict[str, str]={}, remove_after=True):
        super().__init__(field, conditions=conditions, remove_after=remove_after)
        assert pattern is not None
        self.__pattern: str = pattern

    def _extract(self, transaction: Transaction | Subtransaction) -> List[str]:
        field_value = getattr(transaction, self._field, '')
        return re.findall(self.__pattern, field_value) if field_value else []

    def _remove_after(self, transaction: Transaction | Subtransaction) -> Any:
        if getattr(transaction, self._field, None):
            setattr(
                transaction,
                self._field,
                re.sub(self.__pattern, '', getattr(transaction, self._field))
            )


class KeyValueExtractor(Extractor):

    def __init__(self, field: str, kv_pattern: str, conditions: Dict[str, str]={}, remove_after=True):
        super().__init__(field, conditions=conditions, remove_after=remove_after)
        assert kv_pattern is not None
        self.__kv_pattern: str = kv_pattern

    def _extract(self, transaction: Transaction | Subtransaction) -> Dict[str, str]:
        field_value = getattr(transaction, self._field, None)
        return {
            m.group('k'): m.group('v')
            for m in re.finditer(
                self.__kv_pattern,
                field_value
            )
        } if field_value else {}

    def _remove_after(self, transaction: Transaction | Subtransaction) -> Any:
        if getattr(transaction, self._field, None):
            setattr(
                transaction,
                self._field,
                re.sub(self.__kv_pattern, '', getattr(transaction, self._field))
            )


def from_yml_file(filename: Path | str, node: List[str]=['extractors']) -> List[Extractor]:
    assert filename is not None
    if type(filename) == str:
        filename = Path(filename)
    assert filename.exists()
    extractors: List[Extractor] = []
    with open(filename, 'r') as f:
        yamlconf = yaml.safe_load(f)
        for n in node:
            yamlconf = yamlconf.get(n)
        for item in yamlconf:
            extractor = None
            if 'simple' in item:
                extractor = SimpleExtractor(
                    field=item['simple']['field'],
                    pattern=item['simple']['pattern'],
                    conditions=item['simple'].get('conditions', {}),
                    remove_after=item['simple'].get('remove_after', True)
                )
            elif 'keyvalue' in item:
                extractor = KeyValueExtractor(
                    field=item['keyvalue']['field'],
                    kv_pattern=item['keyvalue']['kv_pattern'],
                    remove_after=item['keyvalue'].get('remove_after', True)
                )
            else:
                log.warning(f'unknown extractor {item} -- skipping')
            if extractor:
                extractors.append(extractor)
                log.info(f'loaded extractor {extractor}')
    return extractors

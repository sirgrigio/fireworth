from abc import ABC, abstractmethod
from typing import Dict, List, Any, NamedTuple

from pathlib import Path

import yaml

import re

from src.modules.ynab.api.models.transactions import Subtransaction, Transaction

import logging

from src.modules.ynab.beancount.utils.beancount import BeancountTransaction
from src.modules.ynab.beancount.utils.conditions import StrFieldCondition

log = logging.getLogger(__name__)


class Processor(ABC):

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)

    def __copy(self, obj: Any) -> Any:
        if isinstance(obj, Transaction):
            return Transaction.from_dict(obj.__dict__)
        elif isinstance(obj, Subtransaction):
            return Subtransaction.from_dict(obj.__dict__)
        elif isinstance(obj, BeancountTransaction):
            return BeancountTransaction.from_dict(obj.__dict__)
        else:
            self.log.warning(f'received unknown object to copy of type {type(obj)}')
            return None

    def apply_to(self, obj: Transaction) -> Transaction:
        assert obj is not None
        log.debug(
            f'{self} processing '
            + obj.describe(sep=" >> ")
            if isinstance(obj, Transaction) or isinstance(obj, Subtransaction)
            else obj
        )
        return self._apply_to(obj)

    @abstractmethod
    def can_be_applied_to(self, obj: Any) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def _modify(self, obj: Any):
        raise NotImplementedError()

    def setValue(self, obj: Any, field: str, value: str):
        if value:
            for var in re.findall(r'\$(\w+)', value):
                repl = getattr(obj, var)
                value = re.sub('\$' + var, repl if repl else '', value)
        setattr(obj, field, value)

    def _apply_to(self, obj: Any) -> Any:
        new_stxns = None
        if isinstance(obj, Transaction) and obj.subtransactions:
            new_stxns = self._apply_to_substractions(obj.subtransactions)
        newobj = self.__copy(obj)
        if not new_stxns and not self.can_be_applied_to(newobj):
            log.debug(f'object has not been modified - returning a copy')
            return newobj
        if isinstance(newobj, Transaction) and new_stxns:
            newobj.subtransactions = new_stxns
        if self.can_be_applied_to(newobj):
            self._modify(newobj)
        log.debug(
            'object has been modified: '
            + newobj.describe(sep=" >> ")
            if isinstance(newobj, Transaction) or isinstance(newobj, Subtransaction)
            else newobj
        )
        return newobj

    def _apply_to_substractions(self, list: List[Subtransaction]) -> List[Subtransaction]:
        newlist: List[Subtransaction] = []
        changed = False
        for stxn in list:
            new_stxn: Subtransaction = self._apply_to(stxn)
            newlist.append(new_stxn)
            if new_stxn != stxn:
                changed = True
        return newlist if changed else None

    @staticmethod
    def apply(processors: List["Processor"], obj: Any) -> Any:
        new_t = obj
        for p in processors:
            new_t = p.apply_to(new_t)
        return new_t


class ReplaceProcessor(Processor):

    def __init__(self, field: str, pattern: str, value: str):
        super().__init__()
        self.__field = field
        self.__pattern = pattern
        self.__condition = StrFieldCondition(field, pattern)
        self.__value = value

    def can_be_applied_to(self, obj: Any) -> bool:
        return self.__condition.match(obj)

    def _modify(self, obj: Any):
        self.setValue(
            obj,
            self.__field,
            re.sub(
                self.__pattern,
                self.__value,
                getattr(obj, self.__field)
            )
        )

    def __repr__(self) -> str:
        return f'ReplaceProc({self.__field})["{self.__pattern}" -> "{self.__value}"]'


class IfThenProcessor(Processor):

    def __init__(self, conditions=Dict[str, str], actions=List[Dict[str, str]]):
        super().__init__()
        self.__conditions: List[StrFieldCondition] = [
            StrFieldCondition(f, p) for f, p in conditions.items()
        ]
        self.__actions: List[Dict[str, str]] = [{f: v for f, v in a.items()} for a in actions]

    def can_be_applied_to(self, obj: Any) -> bool:
        for condition in self.__conditions:
            if not condition.match(obj):
                return False
        return True

    def _modify(self, obj: Any):
        for a in self.__actions:
            for field, value in a.items():
                self.setValue(obj, field, value)

    def __repr__(self) -> str:
        conditions = ' and '.join([str(c) for c in self.__conditions])
        actions = '; '.join([
            '; '.join([f'{f} = "{v}"' for f,v in a.items()])
            for a in self.__actions
        ])
        return f'IfThenProc({conditions})' + '{' + actions + '}'


def from_yml_file(filename: Path | str, node: List[str]=['processors']) -> List[Processor]:
    assert filename is not None
    if type(filename) == str:
        filename = Path(filename)
    assert filename.exists()
    processors: List[Processor] = []
    with open(filename, 'r') as f:
        yamlconf = yaml.safe_load(f)
        for n in node:
            yamlconf = yamlconf.get(n)
        for item in yamlconf:
            processor = None
            if 'if' in item:
                processor = IfThenProcessor(
                    conditions=item['if'],
                    actions=item['then']
                )
            elif 'replace' in item:
                processor = ReplaceProcessor(**item['replace'])
            else:
                log.warning(f'{filename}: unknown processor {item} -- skipping')
            if processor:
                processors.append(processor)
                log.info(f'{filename}: loaded processor {processor}')
    return processors

from abc import ABC, abstractmethod
from typing import Dict, List, Any

from pathlib import Path

import yaml

import re

from src.modules.ynab.api.models.transactions import Subtransaction, Transaction

import logging

from src.modules.ynab.beancount.utils.conditions import StrFieldCondition

log = logging.getLogger(__name__)


class Preprocessor(ABC):

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)

    def __copy(self, obj: Transaction | Subtransaction) -> Transaction | Subtransaction:
        if isinstance(obj, Transaction):
            return Transaction.from_dict(obj.__dict__)
        elif isinstance(obj, Subtransaction):
            return Subtransaction.from_dict(obj.__dict__)
        else:
            self.log.warn(f'received unknown object to copy of type {type(obj)}')
            return None

    def apply_to(self, obj: Transaction) -> Transaction:
        assert obj is not None
        log.debug(f'{self} processing {obj.describe(sep=" >> ")}')
        return self._apply_to(obj)

    @abstractmethod
    def can_be_applied_to(self, obj: Transaction | Subtransaction) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def _modify(self, obj: Any):
        raise NotImplementedError()

    def setValue(self, obj: Any, field: str, value: str):
        for var in re.findall(r'\$(\w+)', value):
            repl = getattr(obj, var)
            value = re.sub('\$' + var, repl if repl else '', value)
        setattr(obj, field, value)

    def _apply_to(self, obj: Transaction | Subtransaction) -> Transaction | Subtransaction:
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
        log.debug(f'object has been modified: {newobj.describe(sep=" >> ")}')
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
    def apply(preprocessors: List["Preprocessor"], transaction: Transaction) -> Transaction:
        new_t = transaction
        for p in preprocessors:
            new_t = p.apply_to(new_t)
        return new_t


class ReplacePreprocessor(Preprocessor):

    def __init__(self, field: str, pattern: str, value: str):
        super().__init__()
        self.__field = field
        self.__pattern = pattern
        self.__condition = StrFieldCondition(field, pattern)
        self.__value = value

    def can_be_applied_to(self, obj: Transaction | Subtransaction) -> bool:
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
        return f'ReplacePrep({self.__field})["{self.__pattern}" -> "{self.__value}"]'


class IfThenPreprocessor(Preprocessor):

    def __init__(self, conditions=Dict[str, str], actions=Dict[str, str]):
        super().__init__()
        self.__conditions: List[StrFieldCondition] = [
            StrFieldCondition(f, p) for f, p in conditions.items()
        ]
        self.__actions = {f: v for f, v in actions.items()}

    def can_be_applied_to(self, obj: Transaction | Subtransaction) -> bool:
        for condition in self.__conditions:
            if not condition.match(obj):
                return False
        return True

    def _modify(self, obj: Any):
        for field, value in self.__actions.items():
            self.setValue(obj, field, value)

    def __repr__(self) -> str:
        conditions = ' and '.join([str(c) for c in self.__conditions])
        actions = '; '.join([f'{f} = "{v}"' for f,v in self.__actions.items()])
        return f'IfThenPrep({conditions})' + '{' + actions + '}'


def from_yml_file(filename: Path | str, node: List[str]=['preprocessors']) -> List[Preprocessor]:
    assert filename is not None
    if type(filename) == str:
        filename = Path(filename)
    assert filename.exists()
    preprocessors: List[Preprocessor] = []
    with open(filename, 'r') as f:
        yamlconf = yaml.safe_load(f)
        for n in node:
            yamlconf = yamlconf.get(n)
        for item in yamlconf:
            preprocessor = None
            if 'if' in item:
                preprocessor = IfThenPreprocessor(
                    conditions=item['if'],
                    actions=item['then']
                )
            elif 'replace' in item:
                preprocessor = ReplacePreprocessor(**item['replace'])
            else:
                log.warn(f'unknown preprocessor {item} -- skipping')
            if preprocessor:
                preprocessors.append(preprocessor)
                log.info(f'loaded preprocessor {preprocessor}')
    return preprocessors

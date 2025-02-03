
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.modules.ynab.api.models.transactions import (Subtransaction,
                                                      Transaction)
from src.modules.ynab.beancount.utils.conditions import StrFieldCondition
from src.modules.ynab.beancount.utils.fi_transaction import FITransaction

log = logging.getLogger(__name__)


class PropertyExtractor:

    def __init__(self, properties: List[str]=[], field: str=None, regex: str=None):
        assert properties is not None
        assert len(properties) > 0
        for p in properties:
            assert f'?P<{p}>' in regex, f'regex has no capturing group for property {p}'
        self.__properties = properties
        self.__field = field
        self.__regex = regex

    @property
    def properties(self):
        return self.__properties

    def extract(self, transaction: Transaction | Subtransaction) -> str:
        match = re.match(self.__regex, getattr(transaction, self.__field, ''))
        return {p: match.group(p) for p in self.__properties} if match else None


class Parser(ABC):

    def __init__(self, extractions: List[PropertyExtractor]=[], conditions: Dict[str, str]={}):
        self.log = logging.getLogger(self.__class__.__name__)
        assert extractions is not None
        assert len(extractions) > 0
        self.__extractions = [p for p in extractions]
        self.__conditions: List[StrFieldCondition] = [
            StrFieldCondition(f, p) for f, p in conditions.items()
        ] if conditions else []

    @property
    def _extractions(self):
        return self.__extractions

    @property
    def _conditions(self):
        return self.__conditions

    def _extract(self, transaction: Transaction | Subtransaction) -> Any:
        result = dict()
        for extractor in self.__extractions:
            result = result | extractor.extract(transaction)
        return result

    @abstractmethod
    def _parse(self, transaction: Transaction | Subtransaction) -> Any:
        pass

    def parse(self, transaction: Transaction | Subtransaction) -> Any:
        if all([c.match(transaction) for c in self._conditions]):
            return self._parse(transaction)
        return None


class FinancialInstrumentTransactionParser(Parser):

    def __init__(
            self,
            default_currency: str='EUR',
            extractions: List[PropertyExtractor]=[],
            conditions: Dict[str, str]={},
    ):
        super().__init__(extractions=extractions, conditions=conditions)
        self.__default_currency = default_currency

    def _parse(self, transaction: Transaction | Subtransaction) -> FITransaction:
        fi_params = self._extract(transaction)
        if "currency" not in fi_params or not fi_params["currency"]:
            fi_params["currency"] = self.__default_currency
        return FITransaction.factory(**fi_params)



def from_yml_file(filename: Path | str, node: List[str]=['parsers']) -> List[Parser]:
    assert filename is not None
    if type(filename) == str:
        filename = Path(filename)
    assert filename.exists()
    parsers: List[Parser] = []
    with open(filename, 'r') as f:
        yamlconf = yaml.safe_load(f)
        for n in node:
            yamlconf = yamlconf.get(n)
        for item in yamlconf:
            parser = None
            if 'financial_istrument_transaction' in item:
                elem = item['financial_istrument_transaction']
                parser = FinancialInstrumentTransactionParser(
                    conditions=elem.get('conditions', {}),
                    extractions=[
                        PropertyExtractor(**e)
                        for e in elem.get('extractions')
                    ]
                )
            else:
                log.warning(f'unknown parser {item} -- skipping')
            if parser:
                parsers.append(parser)
                log.info(f'loaded parser {parser}')
    return parsers

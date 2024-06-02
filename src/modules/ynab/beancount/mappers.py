from abc import ABC, abstractmethod
from src.utils.ynab.transaction import YNABTransaction

from pathlib import Path

from typing import Any, Dict, Tuple

import json


class Mapper(ABC):

    @abstractmethod
    def map(self, value: Any, default: Any=None, **kwargs) -> Any:
        raise NotImplementedError()


class SingleValueMapper(Mapper):

    def __init__(self, mappings: Dict[str, str]):
        self.mappings: Dict[str, str] = mappings

    def map(self, value: str, default: str=None) -> str:
        return self.mappings.get(value, default)

    @staticmethod
    def from_json_file(filename: Path) -> "SingleValueMapper":
        assert filename is not None
        assert filename.exists()
        with open(filename, 'r') as f:
            return SingleValueMapper(json.load(f))


class MultiValueMapper(Mapper):

    def __init__(self, mappings: Dict[str, Any]):
        self.mappings: Dict[str, Any] = mappings

    def map(self, value: Tuple[str], default: str=None, default_key: str=None) -> str:
        mapping = self.mappings
        for e in value:
            mapping = mapping.get(e, mapping.get(default_key, default)) \
                if isinstance(mapping, dict) else str(mapping)
        return mapping

    @staticmethod
    def from_json_file(filename: Path) -> "MultiValueMapper":
        assert filename is not None
        assert filename.exists()
        with open(filename, 'r') as f:
            return MultiValueMapper(json.load(f))

import re
from abc import ABC, abstractmethod
from typing import Any


class Condition(ABC):

    @abstractmethod
    def match(self, object: Any) -> bool:
        raise NotImplementedError()


class StrFieldCondition(Condition):

    def __init__(self, field: str, pattern: str):
        super().__init__()
        assert field is not None
        self.__field = field
        self.__pattern = pattern

    def _interpolate(self, obj: Any) -> str:
        if not self.__pattern:
            return self.__pattern
        pattern_int = self.__pattern
        for var in re.findall(r'\$(\w+)', pattern_int):
            repl = getattr(obj, var)
            pattern_int = re.sub('\$' + var, repl if repl else '', pattern_int)
        return pattern_int

    def match(self, object: Any, interpolate=True) -> bool:
        value = getattr(object, self.__field, None)
        pattern = self._interpolate(object) if interpolate else self.__pattern
        return ((not pattern and not value)
            or (pattern and value and re.search(pattern, value)))

    def __repr__(self) -> str:
        return f'{self.__field} ~ "{self.__pattern}"'


class MultiStrFieldCondition(Condition):

    def __init__(self, field_patterns: dict[str, str]):
        super().__init__()
        assert field_patterns is not None and len(field_patterns) > 0
        self.__field_patterns = {
            field: pattern for field, pattern in field_patterns.items()
        }

    def _interpolate(self, obj: Any, pattern: str) -> str:
        if not pattern:
            return pattern
        pattern_int = pattern
        for var in re.findall(r'\$(\w+)', pattern_int):
            repl = getattr(obj, var)
            pattern_int = re.sub('\$' + var, repl if repl else '', pattern_int)
        return pattern_int

    def match(self, object: Any, interpolate=True) -> bool:
        for field, pattern in self.__field_patterns.items():
            value = getattr(object, field, None)
            pattern_to_match = self._interpolate(object, pattern) if interpolate else pattern
            if not (
                (not pattern_to_match and not value)
                or (pattern_to_match and value and re.search(pattern_to_match, value))
            ):
                return False
        return True

    def __repr__(self) -> str:
        conditions = [f'{field} ~ "{pattern}"'
                     for field, pattern in self.__field_patterns.items()]
        return ' AND '.join(conditions)

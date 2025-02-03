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

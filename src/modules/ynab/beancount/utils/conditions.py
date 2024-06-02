

from abc import ABC, abstractmethod
import re
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

    def match(self, object: Any) -> bool:
        value = getattr(object, self.__field, None)
        return ((not self.__pattern and not value)
            or (self.__pattern and value and re.search(self.__pattern, value)))

    def __repr__(self) -> str:
        return f'{self.__field} ~ "{self.__pattern}"'

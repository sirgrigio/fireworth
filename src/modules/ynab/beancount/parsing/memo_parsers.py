from abc import ABC, abstractmethod
import re
from typing import Set

from .utils import travel_name_to_tag


class MemoParser(ABC):

    def __init__(self, memo):
        self._memo = memo

    @abstractmethod
    def extract_payee(self) -> str:
        ...

    @abstractmethod
    def extract_narration(self) -> str:
        ...

    @abstractmethod
    def extract_tags(self) -> Set[str]:
        ...

    @abstractmethod
    def extract_recipients(self) -> Set[str]:
        ...


class EmptyMemoParser(MemoParser):

    def extract_payee(self) -> str:
        return None

    def extract_narration(self) -> str:
        return None

    def extract_tags(self) -> Set[str]:
        return []

    def extract_recipients(self) -> Set[str]:
        return []


class GenericMemoParser(EmptyMemoParser):

    def __init__(self, memo):
        super().__init__(memo)
        self._pattern_payee_narration = r'([@#][\w\-,]+)?((?P<payee>[\w\s]+):)?(?P<narration>[\w\s&\-\(\)\+\']+)'
        self._pattern_recipients = r'@([\w,]+)'
        self._pattern_tags = r'#([\w\-]+)'

    def extract_payee(self) -> str:
        match = re.search(self._pattern_payee_narration, self._memo)
        assert match is not None
        payee = match.group('payee')
        return payee.strip() if payee else match.group('narration').strip()

    def extract_narration(self) -> str:
        match = re.search(self._pattern_payee_narration, self._memo)
        assert match is not None
        payee = match.group('payee')
        return match.group('narration').strip() if payee else None

    def extract_tags(self) -> Set[str]:
        return set(re.findall(self._pattern_tags, self._memo))

    def extract_recipients(self) -> Set[str]:
        groups = re.findall(self._pattern_recipients, self._memo)
        recipients = []
        for g in groups:
            recipients += g.split(',')
        return set(recipients)



class TravelMemoParser(GenericMemoParser):

    def __init__(self, memo):
        super().__init__(memo)
        self._pattern_travel_name = r'TR[VBT][0-9]{4}: [\w&\-\s]+'
        self._pattern_travel_payee = self._pattern_travel_name + r'(:(?P<narration>[\w\s&\-\(\)\+\']+))?'

    def extract_payee(self) -> str:
        return None

    def extract_narration(self) -> str:
        group = re.search(self._pattern_travel_payee, self._memo).group('narration')
        return group.strip() if group else None

    def extract_tags(self) -> Set[str]:
        tags = super().extract_tags()
        match = re.search(self._pattern_travel_name, self._memo)
        assert match is not None
        tags.add(travel_name_to_tag(match.group(0)))
        tags.add('trip')
        return tags



class InvestmentMemoParser(GenericMemoParser):
    pass


def memo_parser(memo: str) -> MemoParser:
    if not memo:
        return EmptyMemoParser('')
    elif re.search(r'TR[VBT][0-9]{4}:', memo):
        return TravelMemoParser(memo)
    elif memo.startswith(('BUY','SEL','MAT','EXC','ACC','COU','DIV')):
        return InvestmentMemoParser(memo)
    else:
        return GenericMemoParser(memo)

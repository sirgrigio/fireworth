import logging
import os
from pathlib import Path
from typing import List

import yaml

from src.modules.ynab.beancount import extractors, mergers, parsers, processors
from src.modules.ynab.beancount.mappers import (MultiValueMapper,
                                                SingleValueMapper)
from src.modules.ynab.beancount.utils.conditions import MultiStrFieldCondition

log = logging.getLogger(__name__)


class Settings:

    def __init__(self, base_path=None, **kwargs):
        log.debug(f'creating settings with base_path={base_path}')
        for k, v in kwargs.items():
            log.debug(f'{k} = {v}')

        self.xfer_ynab_lending_accounts: List[str] = kwargs.get('xfer_ynab_lending_accounts', None)
        self.xfer_lending_accounts: List[str] = kwargs.get('xfer_lending_accounts', None)
        self.xfer_default_payee: str = kwargs.get('xfer_default_payee', None)
        self.xfer_default_lending_payee: str = kwargs.get('xfer_default_lending_payee', None)
        self.xfer_default_payback_payee: str = kwargs.get('xfer_default_payback_payee', None)
        self.xfer_default_borrowing_payee: str = kwargs.get('xfer_default_borrowing_payee', None)
        self.xfer_default_payment_payee: str = kwargs.get('xfer_default_payment_payee', None)

        self.xfer_ynab_financial_instrument_accounts: List[str] = kwargs.get('xfer_ynab_financial_instrument_accounts', None)

        def __get_filename(key):
            filename = kwargs.get(key, None)
            return os.path.join(base_path, filename) if filename else None

        def __load_or_else(filename, path_loader, else_value):
            return path_loader(Path(filename)) if filename else else_value

        self.preprocessors: List[processors.Processor] = __load_or_else(
            __get_filename('preprocessors_file'), processors.from_yml_file, [])
        self.postprocessors: List[processors.Processor] = __load_or_else(
            __get_filename('postprocessors_file'), processors.from_yml_file, [])

        self.mergers: List[mergers.Merger] = __load_or_else(
            __get_filename('mergers_file'), mergers.from_yml_file, [])

        self.mapper_accounts: SingleValueMapper = __load_or_else(
            __get_filename('mapper_accounts_file'), SingleValueMapper.from_json_file, None)
        self.mapper_inflows: SingleValueMapper = __load_or_else(
            __get_filename('mapper_inflows_file'), SingleValueMapper.from_json_file, None)
        self.mapper_expenses: MultiValueMapper = __load_or_else(
            __get_filename('mapper_expenses_file'), MultiValueMapper.from_json_file, None)
        self.mapper_pnl: SingleValueMapper = __load_or_else(
            __get_filename('mapper_pnl_file'), SingleValueMapper.from_json_file, None)

        self.extractors_meta: List[extractors.KeyValueExtractor] = __load_or_else(
            __get_filename('extractors_meta_file'), extractors.from_yml_file, [])
        self.extractors_recipients: List[extractors.SimpleExtractor] = __load_or_else(
            __get_filename('extractors_recipients_file'), extractors.from_yml_file, [])
        self.extractors_tags: List[extractors.SimpleExtractor] = __load_or_else(
            __get_filename('extractors_tags_file'), extractors.from_yml_file, [])

        self.parsers: List[parsers.Parser] = __load_or_else(
            __get_filename('parser_financial_instrument_transactions'), parsers.from_yml_file, [])

        self.skip_conditions = []
        for conditions in kwargs.get('skip', []):
            self.skip_conditions.append(MultiStrFieldCondition(conditions))


    @staticmethod
    def from_yml_file(filename: Path | str, node: List[str]=[]) -> "Settings":
        assert filename is not None
        if type(filename) == str:
            filename = Path(filename)
        assert filename.exists()
        with open(filename, 'r') as f:
            yamlconf = yaml.safe_load(f)
            for n in node:
                yamlconf = yamlconf.get(n)
            return Settings(
                os.path.dirname(
                    os.path.abspath(filename)
                ),
                **yamlconf
            )

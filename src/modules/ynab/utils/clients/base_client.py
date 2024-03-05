import logging
from abc import ABC, abstractmethod


class BaseClient(ABC):
    def __init__(self, api_key: str, base_path="/v1", host="https://api.ynab.com"):
        self.api_key = api_key
        self.base_path = base_path
        self.host = host
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def get(self, endpoint: str):
        raise NotImplementedError()

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json",
        }

    @property
    def base_url(self):
        return self.host + self.base_path

import requests

from .base_client import BaseClient


class DefaultClient(BaseClient):
    def __init__(self, api_key: str, base_path='/v1', host='https://api.ynab.com'):
        super().__init__(api_key, base_path, host)

    def get(self, endpoint: str):
        url = self.base_url + endpoint
        self.logger.debug(f'GET {url}')
        response = requests.get(url, headers=self.headers)
        self.logger.debug(response)
        data = response.json()
        return data

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
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, payload: dict):
        url = self.base_url + endpoint
        self.logger.debug(f'POST {url}')
        response = requests.post(url, json=payload, headers=self.headers)
        self.logger.debug(response)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, payload: dict):
        url = self.base_url + endpoint
        self.logger.debug(f'PUT {url}')
        response = requests.put(url, json=payload, headers=self.headers)
        self.logger.debug(response)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str):
        url = self.base_url + endpoint
        self.logger.debug(f'DELETE {url}')
        response = requests.delete(url, headers=self.headers)
        self.logger.debug(response)
        response.raise_for_status()
        return response.json()

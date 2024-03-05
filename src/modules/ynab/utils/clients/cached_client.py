import json
from typing import Optional

import requests
from redis import Redis

from .default_client import DefaultClient


class CachedClient(DefaultClient):

    def __init__(
            self,
            api_key: str,
            cache_host: str,
            cache_port: int,
            base_path='/v1',
            host='https://api.ynab.com',
            cache_db: int = 0,
            cache_pass: Optional[str] = None,
    ):
        super().__init__(api_key, base_path, host)
        self.redis = Redis(
            host=cache_host,
            port=cache_port,
            db=cache_db,
            password=cache_pass,
        )
        self._cache_ttl: Optional[int] = 3600
        self._keys_prefix: str = 'YNAB_'

    def clear_cache(self) -> None:
        keys_count: int = 0
        for k in self.redis.scan_iter(''.join([self._keys_prefix, '*'])):
            self.redis.delete(k)
            keys_count += 1
        self.logger.info(f'{keys_count} keys deleted from cache')

    def get(self, endpoint: str):
        self.logger.debug(f'Cache lookup for {endpoint}')
        cached_data = self.redis.get(''.join([self._keys_prefix, endpoint]))
        if cached_data:
            self.logger.info('Using cached data')
            data = json.loads(cached_data)
        else:
            self.logger.info('Cached data not found, fetching from remote')
            url = self.base_url + endpoint
            self.logger.debug(f'GET {url}')
            response = requests.get(url, headers=self.headers)
            self.logger.debug(response)
            data = response.json()
            if response.status_code == 200:
                self.redis.set(
                    ''.join([self._keys_prefix, endpoint]),
                    json.dumps(data),
                    self.cache_ttl,
                )
        return data

    @property
    def cache_ttl(self) -> Optional[int]:
        return self._cache_ttl

    @cache_ttl.setter
    def cache_ttl(self, ttl_value: Optional[int]) -> None:
        if ttl_value and ttl_value > 0:
            self._cache_ttl = ttl_value
            self.logger.debug(f'TTL value set to {ttl_value}')
        else:
            self._cache_ttl = None
            self.logger.debug(f'Invalid TTL {ttl_value}, TTL set to None')

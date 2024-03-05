from src.modules.ynab.api.budgets import BudgetsApi
from src.modules.ynab.api.transactions import TransactionsApi
from src.modules.ynab.utils.clients.base_client import BaseClient
from src.modules.ynab.utils.clients.default_client import DefaultClient


class YNAB:
    def __init__(self, api_key: str = None, client: BaseClient = None):
        assert api_key is not None or client is not None

        if client:
            self.client = client
        else:
            self.client = DefaultClient(api_key)

    @property
    def budgets(self):
        return BudgetsApi(self.client)

    @property
    def transactions(self):
        return TransactionsApi(self.client)

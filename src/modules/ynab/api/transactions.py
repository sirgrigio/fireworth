from src.modules.ynab.api.models.transactions import TransactionsResponse
from src.modules.ynab.utils.clients.base_client import BaseClient


class TransactionsApi:

    def __init__(self, client: BaseClient):
        self.client = client

    def get_transactions(self, budget_id: str) -> TransactionsResponse:
        response = self.client.get(f"/budgets/{budget_id}/transactions")
        return TransactionsResponse.from_dict(response)

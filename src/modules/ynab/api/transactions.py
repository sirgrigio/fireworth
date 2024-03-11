import dataclasses
from typing import List

from src.modules.ynab.api.models.transactions import (
    CreateTransactionResponse, Transaction, TransactionsResponse)
from src.modules.ynab.utils.clients.base_client import BaseClient


class TransactionsApi:

    def __init__(self, client: BaseClient):
        self.client = client

    def get_transactions(self, budget_id: str) -> TransactionsResponse:
        response = self.client.get(f"/budgets/{budget_id}/transactions")
        return TransactionsResponse.from_dict(response)

    def create_transactions(self, budget_id: str, transactions: List[Transaction]):
        payload = {"transactions": [dataclasses.asdict(t) for t in transactions]}
        response = self.client.post(f"/budgets/{budget_id}/transactions", payload)
        return CreateTransactionResponse.from_dict(response)

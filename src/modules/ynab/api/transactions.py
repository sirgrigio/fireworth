import dataclasses
from typing import List

from src.modules.ynab.api.models.transactions import (
    CreateTransactionResponse, Transaction, TransactionListResponse,
    TransactionResponse)
from src.modules.ynab.utils.clients.base_client import BaseClient


class TransactionsApi:

    def __init__(self, client: BaseClient):
        self.client = client

    def get_transactions(self, budget_id: str) -> TransactionListResponse:
        response = self.client.get(f"/budgets/{budget_id}/transactions")
        return TransactionListResponse.from_dict(response)

    def create_transactions(self, budget_id: str, transactions: List[Transaction]) -> CreateTransactionResponse:
        payload = {"transactions": [dataclasses.asdict(t) for t in transactions]}
        response = self.client.post(f"/budgets/{budget_id}/transactions", payload)
        return CreateTransactionResponse.from_dict(response)

    def update_transaction(self, budget_id: str, transaction: Transaction) -> TransactionResponse:
        payload = {"transaction": dataclasses.asdict(transaction)}
        print(payload)
        response = self.client.put(f"/budgets/{budget_id}/transactions/{transaction.id}", payload)
        return TransactionResponse.from_dict(response)

    def delete_transaction(self, budget_id: str, transaction_id: str) -> TransactionResponse:
        response = self.client.delete(f"/budgets/{budget_id}/transactions/{transaction_id}")
        return TransactionResponse.from_dict(response)

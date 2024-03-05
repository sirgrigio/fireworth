from src.modules.ynab.utils.clients.base_client import BaseClient
from src.modules.ynab.api.models.budget_summary import BudgetSummaryResponse


class BudgetsApi:
    def __init__(self, client: BaseClient):
        self.client = client

    def get_budgets(self) -> BudgetSummaryResponse:
        response = self.client.get("/budgets")
        return BudgetSummaryResponse.from_dict(response)

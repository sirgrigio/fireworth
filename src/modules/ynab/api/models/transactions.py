from dataclasses import dataclass
from typing import Any, List, Optional

from src.modules.ynab.utils import parsers


@dataclass
class Subtransaction:
    id: str
    transaction_id: str
    amount: int
    memo: Optional[str]
    payee_id: Optional[str]
    category_id: Optional[str]
    transfer_account_id: Optional[str]
    transfer_transaction_id: Optional[str]
    payee_name: Optional[str]
    category_name: Optional[str]
    deleted: bool
    account_name: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> "Subtransaction":
        assert isinstance(obj, dict)
        sub_transaction_id = parsers.from_str(obj.get("id"))
        transaction_id = parsers.from_str(obj.get("transaction_id"))
        amount = parsers.from_int(obj.get("amount"))
        memo = parsers.from_str(obj.get("memo"), True)
        payee_id = parsers.from_str(obj.get("payee_id"), True)
        category_id = parsers.from_str(obj.get("category_id"), True)
        transfer_account_id = parsers.from_str(obj.get("transfer_account_id"), True)
        transfer_transaction_id = parsers.from_str(obj.get("transfer_transaction_id"), True)
        payee_name = parsers.from_str(obj.get("payee_name"), True)
        category_name = parsers.from_str(obj.get("category_name"), True)
        deleted = parsers.from_bool(obj.get("deleted"))
        account_name = parsers.from_str(obj.get("account_name"), True)
        return Subtransaction(
            sub_transaction_id,
            transaction_id,
            amount,
            memo,
            payee_id,
            category_id,
            transfer_account_id,
            transfer_transaction_id,
            payee_name,
            category_name,
            deleted,
            account_name
        )

    def describe(self, **kwargs) -> str:
        return '|'.join([
            str(self.account_name),
            str(self.payee_name),
            str(self.category_name),
            str(self.memo),
            str(self.amount)
        ])


@dataclass
class Transaction:
    id: str
    date: str
    amount: int
    memo: Optional[str]
    cleared: str
    approved: bool
    flag_color: Optional[str]
    account_id: str
    payee_id: Optional[str]
    category_id: Optional[str]
    transfer_account_id: Optional[str]
    transfer_transaction_id: Optional[str]
    matched_transaction_id: Optional[str]
    import_id: Optional[str]
    deleted: bool
    account_name: str
    payee_name: Optional[str]
    category_name: Optional[str]
    subtransactions: List[Subtransaction]

    @staticmethod
    def from_dict(obj: Any) -> "Transaction":
        assert isinstance(obj, dict)
        transaction_id = parsers.from_str(obj.get("id"))
        date = parsers.from_str(obj.get("date"))
        amount = parsers.from_int(obj.get("amount"))
        memo = parsers.from_str(obj.get("memo"), True)
        cleared = parsers.from_str(obj.get("cleared"))
        approved = parsers.from_bool(obj.get("approved"))
        flag_color = parsers.from_str(obj.get("flag_color"), True)
        account_id = parsers.from_str(obj.get("account_id"))
        payee_id = parsers.from_str(obj.get("payee_id"), True)
        category_id = parsers.from_str(obj.get("category_id"), True)
        transfer_account_id = parsers.from_str(obj.get("transfer_account_id"), True)
        transfer_transaction_id = parsers.from_str(obj.get("transfer_transaction_id"), True)
        matched_transaction_id = parsers.from_str(obj.get("matched_transaction_id"), True)
        import_id = parsers.from_str(obj.get("import_id"), True)
        deleted = parsers.from_bool(obj.get("deleted"))
        account_name = parsers.from_str(obj.get("account_name"))
        payee_name = parsers.from_str(obj.get("payee_name"), True)
        category_name = parsers.from_str(obj.get("category_name"), True)
        subtransactions = parsers.from_list(
            lambda o: Subtransaction.from_dict(
                o.__dict__ if isinstance(o, Subtransaction) else o
            ),
            obj.get("subtransactions")
        )
        for s in subtransactions:
            s.account_name = account_name
        return Transaction(
            transaction_id,
            date,
            amount,
            memo,
            cleared,
            approved,
            flag_color,
            account_id,
            payee_id,
            category_id,
            transfer_account_id,
            transfer_transaction_id,
            matched_transaction_id,
            import_id,
            deleted,
            account_name,
            payee_name,
            category_name,
            subtransactions,
        )

    def describe(self, sep: str='\n  ') -> str:
        repr = '|'.join([
            str(self.date),
            str(self.account_name),
            str(self.payee_name),
            str(self.category_name),
            str(self.memo),
            str(self.amount)
        ])
        for s in self.subtransactions:
            repr += f'{sep}{s.describe()}'
        return repr


@dataclass
class TransactionListData:
    transactions: List[Transaction]

    @staticmethod
    def from_dict(obj: Any) -> "TransactionListData":
        assert isinstance(obj, dict)
        transactions = parsers.from_list(Transaction.from_dict, obj.get("transactions"))
        return TransactionListData(transactions)


@dataclass
class TransactionData:
    transaction: Transaction

    @staticmethod
    def from_dict(obj: Any) -> "TransactionData":
        assert isinstance(obj, dict)
        transaction = Transaction.from_dict(obj.get("transaction"))
        return TransactionData(transaction)


@dataclass
class TransactionListResponse:
    data: TransactionListData

    @staticmethod
    def from_dict(obj: Any) -> "TransactionListResponse":
        assert isinstance(obj, dict)
        data = TransactionListData.from_dict(obj.get("data"))
        return TransactionListResponse(data)


@dataclass
class TransactionResponse:
    data: TransactionData

    @staticmethod
    def from_dict(obj: Any) -> "TransactionResponse":
        assert isinstance(obj, dict)
        data = TransactionData.from_dict(obj.get("data"))
        return TransactionResponse(data)


@dataclass
class CreateTransactionResponse:
    transaction_ids: List[str]
    transactions: List[Transaction]
    duplicate_import_ids: List[str]

    @staticmethod
    def from_dict(obj: Any) -> "CreateTransactionResponse":
        assert isinstance(obj, dict)
        data = obj.get("data")
        transaction_ids = parsers.from_list(
            parsers.from_str, data.get("transaction_ids")
        )
        transactions = parsers.from_list(
            Transaction.from_dict, data.get("transactions")
        )
        duplicate_import_ids = parsers.from_list(
            parsers.from_str, data.get("duplicate_import_ids")
        )

        return CreateTransactionResponse(
            transaction_ids, transactions, duplicate_import_ids
        )

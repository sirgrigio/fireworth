from src.utils.ynab.memo import parse_memo

from datetime import datetime, date as datetype
import math


class YNABTransaction:

    def __init__(
            self,
            account: str,
            date: datetype,
            payee: str,
            category_group: str,
            category: str,
            memo: str,
            currency: str,
            amount: float,
            is_transfer: bool,
            target_account: str
    ):
        self.account: str = account
        self.date: datetype = date
        self.payee: str = payee
        self.category_group: str = category_group
        self.category: str = category
        self.memo: str = memo
        self.currency: str = currency
        self.amount: float = amount
        self.is_transfer: bool = is_transfer
        self.target_account: str = target_account

    def to_ledger(self, currency: str='EUR'):
        currency = self.currency if self.currency else currency
        extra = parse_memo(self.memo, self.amount, currency)
        accsrc = self.account
        accdst = self.target_account
        if self.account == 'Investments':
            extra_acc = extra.accdst if self.amount > 0 else extra.accsrc
            accsrc = extra_acc if extra_acc else extra.symbol
        if self.target_account == 'Investments':
            extra_acc = extra.accsrc if self.amount > 0 else extra.accdst
            accdst = extra.accdst if extra.accdst else extra.symbol
        return {
            'date': self.date,
            'account': accsrc,
            'target_account': accdst,
            'linked_account': extra.symbol if extra else None,
            'category_group': self.category_group,
            'category': self.category,
            'payee': self.payee,
            'memo': self.memo,
            'amount': extra.amount if extra and self.is_transfer else self.amount,
            'currency': extra.currency if extra else currency,
            'quantity': extra.quantity if extra else None,
            'unit_price': extra.unit_price if extra else None,
            'is_transfer': self.is_transfer,
            'is_symbol': accsrc == extra.symbol if extra else False,
        }


def from_csv(
            account: str,
            _flag: str,
            date: str,
            payee: str,
            _category_group_category: str,
            category_group: str,
            category: str,
            memo: str,
            outflow: str,
            inflow: str,
            _cleared: str
    ):
        payee = payee.replace('Transfer from', 'Transfer')
        date = datetime.strptime(date, '%d/%m/%Y').date()
        amount = float(inflow[1:]) - float(outflow[1:])
        is_transfer = payee.startswith('Transfer :') or payee.startswith('FCY-XFR :')
        target_account = None
        currency = None
        if payee.startswith('Transfer :'):
            # transfer to/from EUR checking/deposit account
            target_account = payee.split(':')[1].strip()
        if payee.startswith('FCY-XFR :'):
            # transfer to/from foreign currency account
            account = payee.split(':')[1].strip()
            target_account = payee.split(':')[2].strip()
        if payee.startswith('FCY-EXP :'):
            # expense from foreign currency account
            account = payee.split(':')[1].strip()
            payee = payee.split(':')[2].strip()
            ## get memo portion with correct amount, e.g.: USD:3.95
            fcy_amount = memo.split(' ')[0].strip()
            memo = memo.replace(fcy_amount, '').strip()
            currency = fcy_amount.split(':')[0].strip()
            amount = math.copysign(float(fcy_amount.split(':')[1]), amount)
        return YNABTransaction(
            account,
            date,
            payee,
            category_group,
            category,
            memo,
            currency,
            amount,
            is_transfer,
            target_account
        )

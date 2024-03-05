_ACCOUNT_MAPPING = {
    'Revolut': 'Assets:CheckingAccounts:Revolut',
    'VISA Fineco': 'Liabilities:CreditCards:VISAFineco',
    'AMEX Blue': 'Liabilities:CreditCards:AMEXBlue',
    'CSRPBI': 'Assets:CheckingAccounts:CSRPBI',
    'IKEA Loan': 'Liabilities:Loans:IKEA',
    'Findomestic Loan': 'Liabilities:Loans:Findomestic',
    'Fineco': 'Assets:CheckingAccounts:Fineco',
    'PayPal': 'Assets:CheckingAccounts:PayPal',
    'Retirement': 'Retirement',
    'CSR Personal Loan': 'Liabilities:Loans:CSRPBI',
    'Lending': 'Assets:Lending',
    'Investments': 'Assets:Investments',
    'Cash': 'Assets:Cash',
    'Family Loan': 'Liabilities:Loans:Family',
    'Kraken': 'Assets:CheckingAccounts:Kraken',
    'Time Deposit': 'Assets:SavingAccounts:TimeDeposit',
    'Car Loan': 'Liabilities:Loans:ToyotaFS',
    'FCA Bank': 'Assets:SavingAccounts:FCABank',
}


def map_account(account: str) -> str:
    return _ACCOUNT_MAPPING[account]

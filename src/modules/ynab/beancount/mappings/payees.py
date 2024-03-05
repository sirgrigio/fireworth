from typing import Callable

INFLOW_PAYEE_MAPPING = {
    'Cashback': lambda a: (a, 'Income:Cashback'),
    'Coupon': None,
    'Day Trading': None,
    'Dividends': None,
    'Gambling': lambda a: (a, 'Income:Gambling'),
    'Interests': lambda a: (a, 'Income:Interests'),
    'Liquidation': lambda a: (a, 'Income:Paychecks:Over'),
    'Paycheck': lambda a: (a, 'Income:Paychecks:BdI'),
    'Reconciliation Balance Adjustment': lambda a: (a, 'Equity:ReconciliationBalanceAdjustment'),
    'Starting Balance': lambda a: (a, 'Equity:OpeningBalance'),
    'Transfer : Investments': None,
    'Transfer : Lending': None,
    'Transfer from: CSR Personal Loan': lambda a: (a, 'Liabilities:Loans:CSRPBI'),
    'Transfer from: Family Loan': lambda a: (a, 'Liabilities:Loans:Family'),
    'Transfer from: Findomestic Loan': lambda a: (a, 'Liabilities:Loans:Findomestic'),
    'Transfer from: IKEA Loan': lambda a: (a, 'Liabilities:Loans:IKEA'),
    'Welfare Credit': lambda _: ('Assets:CompanyWelfare', 'Income:CompanyWelfare:BDI')
}

def map_inflow(payee: str) -> Callable[[str], tuple[str, str]]:
    return INFLOW_PAYEE_MAPPING[payee]

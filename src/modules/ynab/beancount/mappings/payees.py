from typing import Callable

INFLOW_PAYEE_MAPPING = {
    'Cashback': lambda t: ('Income:Cashback', t.account_name),
    'Coupon': None,
    'Day Trading': lambda t: ('Income:PnL', t.account_name),
    'Dividends': None,
    'Gambling': lambda t: ('Income:Gambling', t.account_name),
    'Interests': lambda t: (f'Income:Interests:{t.memo.title().replace(" ","") if t.memo else t.account_name}', t.account_name),
    'Item Sale': lambda t: ('Income:ItemSales', t.account_name),
    'Liquidation': lambda t: ('Income:Paychecks:Over', t.account_name),
    'Paycheck': lambda t: (f'Income:Paychecks:{t.memo}', t.account_name),
    'Reconciliation Balance Adjustment': lambda t: ('Equity:ReconciliationBalanceAdjustment', t.account_name),
    'Starting Balance': lambda t: ('Equity:OpeningBalance', t.account_name),
    'Transfer : Investments': None,
    'Transfer : Lending': None,
    'Transfer from: CSR Personal Loan': lambda t: ('Liabilities:Loans:CSRPBI', t.account_name),
    'Transfer from: Family Loan': lambda t: ('Liabilities:Loans:Family', t.account_name),
    'Transfer from: Findomestic Loan': lambda t: ('Liabilities:Loans:Findomestic', t.account_name),
    'Transfer from: IKEA Loan': lambda t: ('Liabilities:Loans:IKEA', t.account_name),
    'Welfare Credit': lambda _: ('Income:CompanyWelfare:BdI', 'Assets:CompanyWelfare')
}

def map_inflow(payee: str) -> Callable[[str], tuple[str, str]]:
    return INFLOW_PAYEE_MAPPING[payee]

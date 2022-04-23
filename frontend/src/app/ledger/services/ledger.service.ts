import { Injectable } from '@angular/core';
import { DateTime } from 'luxon';
import { Account, AccountType, AccountTypeGroup} from 'src/app/shared/models/account.model';
import { Category, CategoryGroup } from 'src/app/shared/models/category.model';
import { Payee, Transaction } from 'src/app/shared/models/transaction.model';

@Injectable({
  providedIn: 'root'
})
export class LedgerService {

  constructor() { }

  public getAccountTypeGroups(): AccountTypeGroup[] {
    return [
      new AccountTypeGroup(1, 'CASH', [
        new AccountType(1, 1, 'CASH'),
        new AccountType(2, 1, 'CHECKING_ACCOUNT'),
        new AccountType(3, 1, 'SAVINGS_ACCOUNT'),
      ]),
      new AccountTypeGroup(2, 'CREDIT', [
        new AccountType(4, 2, 'CREDIT_CARD'),
        new AccountType(5, 2, 'LOAN'),
        new AccountType(6, 2, 'MORTGAGE'),
        new AccountType(7, 3, 'LENDING'),        
      ]),
      new AccountTypeGroup(3, 'PROPERTY', [
        new AccountType(8, 3, 'REAL_ESTATE'),
        new AccountType(18, 3, 'COLLECTIBLE')
      ]),
      new AccountTypeGroup(4, 'SECURITY', [
        new AccountType(9, 4, 'BOND'),
        new AccountType(10, 4, 'COMMODITY'),
        new AccountType(11, 4, 'CRYPTO'),
        new AccountType(12, 4, 'ETC'),
        new AccountType(13, 4, 'ETF'),
        new AccountType(14, 4, 'MUTUAL_FUND'),
        new AccountType(15, 4, 'PRIVATE_EQUITY'),
        new AccountType(16, 4, 'STOCK'),
        new AccountType(17, 4, 'STRUCTURED_NOTE'),
      ])
    ];
  }

  public getAccounts(): Account[] {
    return [
      new Account(1, 2, 'CASH', 'CHECKING_ACCOUNT', 'WallyBank', 'EUR', new Map()),
      new Account(2, 2, 'CASH', 'CHECKING_ACCOUNT', 'LollyBank', 'USD', new Map()),
      new Account(3, 11, 'SECURITY', 'CRYPTO', 'Bitcoin', 'BTC', new Map()),
      new Account(4, 16, 'SECURITY', 'STOCK', 'Tesla', 'USD', new Map(), 'TLSA'),
    ];
  }

  public getCategoryGroups(): CategoryGroup[] {
    return [
      new CategoryGroup(1, 'Living', [
        new Category(1, 1, 'Living', 'Rent'),
        new Category(2, 1, 'Living', 'Utilities'),
        new Category(3, 1, 'Living', 'Groceries'),
      ]),
      new CategoryGroup(2, 'Discretionary', [
        new Category(4, 2, 'Discretionary', 'Multimedia'),
        new Category(5, 2, 'Discretionary', 'Eating Out'),
      ]),
    ];
  }

  public getPayees(): Payee[] {
    return [
      new Payee(1, 'EXPENSE', 'Rent'),
      new Payee(2, 'EXPENSE', 'Electricity Bill'),
      new Payee(3, 'EXPENSE', 'Grocery Store'),
      new Payee(4, 'EXPENSE', 'Book'),
      new Payee(5, 'EXPENSE', 'Restaurant'),
      new Payee(6, 'TRANSFER', 'Transfer: LollyBank', 2),
      new Payee(7, 'TRANSFER', 'Transfer: WallyBank', 1),
      new Payee(8, 'TRADE', 'Trade: Tesla', 4),
      new Payee(9, 'TRADE', 'Trade: LollyBank', 2)
    ];
  }

  public getTransations(): Transaction[] {
    return [
      Transaction.make(1, DateTime.now(), 1, 'WallyBank', new Payee(1, 'EXPENSE', 'Rent'), new Category(1, 1, 'Living', 'Rent'), null, 'EUR', -600),
      Transaction.make(2, DateTime.now(), 1, 'WallyBank', new Payee(2, 'EXPENSE', 'Electricity Bill'), new Category(2, 1, 'Living', 'Utilities'), null, 'EUR', -290),
      Transaction.make(3, DateTime.now(), 1, 'WallyBank', new Payee(3, 'EXPENSE', 'Grocery Store'), new Category(3, 1, 'Living', 'Groceries'),  null, 'EUR', -150),
      Transaction.make(4, DateTime.now(), 2, 'LollyBank', new Payee(4, 'EXPENSE', 'Book'), new Category(4, 2, 'Discretionary', 'Multimedia'), null, 'USD', -10),
      Transaction.make(5, DateTime.now(), 1, 'WallyBank', new Payee(5, 'EXPENSE', 'Restaurant'), new Category(5, 2, 'Discretionary', 'Eating Out'), null, 'EUR', -40),
      Transaction.make(6, DateTime.now(), 1, 'WallyBank', new Payee(6, 'TRANSFER', 'Transfer: LollyBank', 2), null, null, 'EUR', -100, 1.2, null, null, 7),
      Transaction.make(7, DateTime.now(), 2, 'LollyBank', new Payee(7, 'TRANSFER', 'Transfer: WallyBank', 1), null, null, 'USD', 120, 0.83, null, null, 6),
      Transaction.make(8, DateTime.now(), 2, 'LollyBank', new Payee(8, 'TRADE', 'Trade: Tesla', 4), null, null, 'USD', -1000, null, 500, 2, 9),
      Transaction.make(9, DateTime.now(), 4, 'Tesla', new Payee(6, 'TRADE', 'Trade: LollyBank', 2), null, null, 'USD', 1000, null, 500, 2, 8),
    ];
  }

  public getCurrencies(): string[] {
    return [
      'EUR',
      'USD',
      'BTC'
    ];
  }

  public getAssetClasses(): string[] {
    return [
      'ALTERNATIVE',
      'BONDS',
      'CCE',
      'COMMODITIES',
      'EQUITIES',
      'REAL_ESTATE',
    ]
  }
}

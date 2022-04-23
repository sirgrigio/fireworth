import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { columnGroupWidths, ColumnMode, SelectionType } from '@swimlane/ngx-datatable';
import { DateTime } from 'luxon';
import { Account } from 'src/app/shared/models/account.model';
import { Category, CategoryGroup } from 'src/app/shared/models/category.model';
import { Payee, Transaction } from 'src/app/shared/models/transaction.model';
import { LedgerService } from '../services/ledger.service';

@Component({
  selector: 'app-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.scss']
})
export class TransactionsComponent implements OnInit {

  @ViewChild('transactionsTable') _table: any;
  _columnMode = ColumnMode;
  _selectionType = SelectionType;

  accounts: Account[] = [];
  categoryGroups: CategoryGroup[] = [];
  categories: Category[] = [];
  payees: Payee[] = [];
  currencies: string[] = []
  @Input() transactions: Transaction[] = [];
  selected: Transaction[] = [];

  editing: { [key: number]: boolean } = {};
  _editingTxn?: Transaction;


  constructor(private ledgerService: LedgerService) { }

  ngOnInit(): void {
    this.accounts = this.ledgerService.getAccounts();
    this.categoryGroups = this.ledgerService.getCategoryGroups();
    this.categories = this.categoryGroups.map(e => e.categories || []).reduce((a, b) => a.concat(b));
    this.payees = this.ledgerService.getPayees();
    this.currencies = this.ledgerService.getCurrencies();
  }

  txn(i: number): Transaction | undefined {
    return this.editing[i] ? this._editingTxn : this.transactions[i];
  }

  getTxnAccount(transaction: Transaction): Account | undefined {
    return this.accounts.find(e => e.accountId == transaction.accountId);
  }

  setTxnDate(date?: DateTime) {
    if (this._editingTxn) {
      this._editingTxn.date = date ? date : this._editingTxn.date;
    }
  }

  setTxnAccount(account?: Account) {
    if (this._editingTxn) {
      this._editingTxn.accountId = account?.accountId;
      this._editingTxn.accountName = account?.name;
    }
  }

  setTxnPayee(payee?: Payee) {
    if (this._editingTxn) {
      this._editingTxn.payee = payee ? payee : this._editingTxn.payee;
    }
  }

  setTxnCategory(category?: Category) {
    if (this._editingTxn) {
      this._editingTxn.category = category ? category : this._editingTxn.category;
    }
  }

  setTxnMemo(memo?: string | null) {
    if (this._editingTxn) {
      this._editingTxn.memo = memo || null;
    }
  }


  setTxnAmount(outflow: boolean, amount?: number) {
    if (this._editingTxn) {
      this._editingTxn.amount = (outflow ? -1 : 1) * (amount ?? 0);
    }
  }

  setTxnCurrency(outflow: boolean, currency?: string) {
    if (this._editingTxn) {
      this._editingTxn.currency = currency ? currency : this._editingTxn.currency;
    }
  }

  setTxnExchangeRate(outflow: boolean, exchangeRate?: number) {
    if (this._editingTxn) {
      this._editingTxn.exchangeRate = exchangeRate;
    }
  }

  setTxnUnitPrice(outflow: boolean, unitPrice?: number) {
    if (this._editingTxn) {
      this._editingTxn.unitPrice = unitPrice;
      this._editingTxn.amount = (outflow ? -1 : 1)
        * (unitPrice ?? 0) * (this._editingTxn.quantity ?? 0)
    }
  }

  setTxnQuantity(outflow: boolean, quantity?: number) {
    if (this._editingTxn) {
      this._editingTxn.quantity = quantity;
      this._editingTxn.amount = (outflow ? -1 : 1)
        * (this._editingTxn.unitPrice ?? 0) * (quantity ?? 0)
    }
  }

  startEditing(row: any, rowIndex: number) {
    if (!this.editing[rowIndex]) {
      this.editing[rowIndex] = true;
      this._table.rowDetail.toggleExpandRow(row);
      this._editingTxn = new Transaction(this.transactions[rowIndex]);
    }
  }

  doneEditing(row: any, cancel = false) {
    for (let i in this.editing) {
      this.transactions[i] = new Transaction(
        !cancel ? this._editingTxn : this.transactions[i]
      );
    }
    this.editing = {};
    this._table.rowDetail.toggleExpandRow(row);
    this.transactions = [...this.transactions];
  }

  rowClass = (row: any) => {
    return { 'editing': this.editing[this.transactions.indexOf(row)] };
  }

  cellClass = (arg: { row: any, column: any, value: any }) => {
    const editing = this.editing[this.transactions.indexOf(arg.row)];
    return {
      'py-1': true,
      'pe-1': arg.column.name?.length > 0,
      'ps-0': arg.column.name?.length > 0,
      'ngx-datatable-cell-editing': editing,
    };
  }
}

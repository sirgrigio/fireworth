import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { Account } from 'src/app/shared/models/account.model';
import { Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-txn-edit-amount',
  templateUrl: './txn-edit-amount.component.html',
  styleUrls: ['./txn-edit-amount.component.scss']
})
export class TxnEditAmountComponent implements OnInit, OnChanges {

  @Input() outflow: boolean = true;
  @Input() transaction?: Transaction;
  @Input() accounts?: Account[];
  @Input() currencies?: string[];
  @Input() placeholder?: string;
  @Input() readonly: boolean = true;

  @Output() currencyChange = new EventEmitter<{ currency?: string, outflow: boolean }>();
  @Output() amountChange = new EventEmitter<{ amount?: number, outflow: boolean }>();
  @Output() exchangeRateChange = new EventEmitter<{ exchangeRate?: number, outflow: boolean }>();
  @Output() unitPriceChange = new EventEmitter<{ unitPrice?: number, outflow: boolean }>();
  @Output() quantityChange = new EventEmitter<{ quantity?: number, outflow: boolean }>();

  _amountExpr?: string;
  _exchangeRateExpr?: string;
  _unitPriceExpr?: string;
  _quantityExpr?: string;

  constructor() { }

  ngOnInit(): void {
    this.updateExpressions();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!changes.readonly.firstChange && changes.readonly.currentValue) {
      this.updateExpressions();
    }
  }

  private updateExpressions() {
    this._amountExpr = this.transaction?.amount?.toString();
    this._exchangeRateExpr = this.transaction?.exchangeRate?.toString();
    this._unitPriceExpr = this.transaction?.unitPrice?.toString();
    this._quantityExpr = this.transaction?.quantity?.toString();
  }

  get absAmount(): number | null | undefined {
    return this.transaction?.amount
      ? Math.abs(this.transaction.amount)
      : this.transaction?.amount;
  }

  onAmountChange() {
    const amount = this.round(this.evalExpr(this._amountExpr));
    this.amountChange.emit({
      amount: amount ? Math.abs(amount) : 0,
      outflow: this.outflow
    });
  }

  onCurrencyChange(currency?: string) {
    this.currencyChange.emit({
      currency: currency,
      outflow: this.outflow
    });
  }

  onExchangeRateChange() {
    this.exchangeRateChange.emit({
      exchangeRate: this.round(this.evalExpr(this._exchangeRateExpr), 8),
      outflow: this.outflow
    });
  }

  onUnitPriceChange() {
    this.unitPriceChange.emit({
      unitPrice: this.round(this.evalExpr(this._unitPriceExpr), 8),
      outflow: this.outflow
    });
  }

  onQuantityChange() {
    this.quantityChange.emit({
      quantity: this.round(this.evalExpr(this._quantityExpr), 8),
      outflow: this.outflow
    });
  }

  private round(value?: number, precision: number = 2): number | undefined {
    if (value == null) {
      return undefined;
    }
    if (precision <= 0) {
      return Math.round(value);
    }
    const tho = 10 ** precision;
    return Math.round(value * tho) / tho;
  }

  private evalExpr(expression?: string): number | undefined {
    try {
      const sanitized = expression?.replace(/[^0-9\-\+\.\*\/]/, '');
      return sanitized ? eval(sanitized) : undefined;
    } catch (e) {
      return undefined;
    }
  }

  exchangeRateNeeded() {
    const linkedAccountId = this.transaction?.payee?.linkedAccountId;
    return (
      linkedAccountId
      && this.accounts?.find(
        a => a.accountId == linkedAccountId
      )?.currency != this.transaction?.currency
    ) || (
        this.accounts?.find(
          a => a.accountId == this.transaction?.accountId
        )?.currency != this.transaction?.currency
      );
  }

  filterUserInput(key: any): boolean {
    const char = key.charCode;
    return (
      (char > 47 && char < 58)  // digits ([0-9])
      || char == 42  // multiply (*)
      || char == 43  // add (+)
      || char == 45  // subtract (-)
      || char == 46  // decimal (.)
      || char == 47  // divide (/)
    );
  }
}

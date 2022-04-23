import { Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { Account } from 'src/app/shared/models/account.model';
import { Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-txn-edit-account',
  templateUrl: './txn-edit-account.component.html',
  styleUrls: ['./txn-edit-account.component.scss']
})
export class TxnEditAccountComponent implements OnInit, OnChanges {

  @ViewChild('typehead') typeheadRef?: ElementRef;

  @Input() transaction?: Transaction;
  @Input() accounts?: Account[];
  @Input() readonly: boolean = true;

  @Output() accountChange: EventEmitter<Account> = new EventEmitter();

  _preview?: Account;

  constructor() { }

  ngOnInit(): void {
    this.updatePreview();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.typeheadRef) {
      if (changes.transaction.currentValue) {
        this.typeheadRef.nativeElement.value = changes.transaction.currentValue.accountName;
      }
    }
    if (!changes.readonly.firstChange && changes.readonly.currentValue) {
      this.updatePreview();
    }
  }

  private updatePreview() {
    this._preview = this.accounts?.find(a => a.accountId == this.transaction?.accountId);
  }

  onAccountChange(account: Account) {
    this._preview = account;
    this.accountChange.emit(account);
  }

  onBlur() {
    this.accountChange.emit(this._preview);
    if (!this._preview && this.typeheadRef) {
      this.typeheadRef.nativeElement.value = null;
    }
  }
}

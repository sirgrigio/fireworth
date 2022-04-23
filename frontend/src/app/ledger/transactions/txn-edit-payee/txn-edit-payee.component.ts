import { Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { Payee, Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-txn-edit-payee',
  templateUrl: './txn-edit-payee.component.html',
  styleUrls: ['./txn-edit-payee.component.scss']
})
export class TxnEditPayeeComponent implements OnInit, OnChanges {

  @ViewChild('typehead') typeheadRef?: ElementRef;

  @Input() transaction?: Transaction;
  @Input() payees?: Payee[];
  @Input() readonly: boolean = true;

  @Output() payeeChange: EventEmitter<Payee> = new EventEmitter();

  _preview?: Payee;

  constructor() { }

  ngOnInit(): void {
    this.updatePreview();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.typeheadRef) {
      if (changes.transaction.currentValue) {
        this.typeheadRef.nativeElement.value = changes.transaction.currentValue.payee.name;
      }
    }
    if (!changes.readonly.firstChange && changes.readonly.currentValue) {
      this.updatePreview();
    }
  }

  private updatePreview() {
    this._preview = this.transaction?.payee ?? undefined;
  }

  onPayeeChange(payee: Payee) {
    this._preview = payee;
    this.payeeChange.emit(payee);
  }

  onBlur() {
    this.payeeChange.emit(this._preview);
    if (!this._preview && this.typeheadRef) {
      this.typeheadRef.nativeElement.value = null;
    }
  }
}

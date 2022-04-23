import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-txn-edit-memo',
  templateUrl: './txn-edit-memo.component.html',
  styleUrls: ['./txn-edit-memo.component.scss']
})
export class TxnEditMemoComponent implements OnInit {

  @Input() transaction?: Transaction;
  @Input() readonly: boolean = true;

  @Output() memoChange: EventEmitter<string> = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  onMemoChange(memo: string) {
    this.memoChange.emit(memo);
  }

}

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DateTime } from 'luxon';
import { BsDatepickerConfig } from 'ngx-bootstrap/datepicker';
import { Transaction } from 'src/app/shared/models/transaction.model';

@Component({
  selector: 'app-txn-edit-date',
  templateUrl: './txn-edit-date.component.html',
  styleUrls: ['./txn-edit-date.component.scss']
})
export class TxnEditDateComponent implements OnInit {

  @Input() transaction?: Transaction;
  @Input() readonly: boolean = true;

  @Output() dateChange: EventEmitter<DateTime> = new EventEmitter();

  bsConfig?: Partial<BsDatepickerConfig>;

  constructor() { }

  ngOnInit(): void {
    this.bsConfig = Object.assign({}, {
      containerClass: 'theme-default',
      dateInputFormat: 'YYYY-MM-DD',
      isAnimated: true,
    });
  }

  onDateChange(date?: Date) {
    this.dateChange.emit(date? DateTime.fromJSDate(date) : undefined);
  }
}

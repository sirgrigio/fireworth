import { Component, Input, OnInit } from '@angular/core';
import { BalanceSheet } from '../statements.models';

@Component({
  selector: 'app-balance-sheet',
  templateUrl: './balance-sheet.component.html',
  styleUrls: ['./balance-sheet.component.scss']
})
export class BalanceSheetComponent implements OnInit {

  @Input() balanceSheet?: BalanceSheet;

  constructor() { }

  ngOnInit(): void {
  }

}

import { Component, OnInit } from '@angular/core';
import { PeriodFilter } from '../shared/components/period-picker/period-filter.model';
import { StatementsService } from './services/statements.service';
import { BalanceSheet } from './statements.models';


@Component({
  selector: 'app-statements',
  templateUrl: './statements.component.html',
  styleUrls: ['./statements.component.scss']
})
export class StatementsComponent implements OnInit {

  balanceSheet?: BalanceSheet;

  constructor(private statementsService: StatementsService) { }

  ngOnInit(): void {
  }

  onPeriodFilterChange(filter?: PeriodFilter) {
    if (filter) {
      this.balanceSheet = this.statementsService.getBalanceSheet(
        filter.from,
        filter.to,
        filter.byQuarter
      );
    }
  }
  
}

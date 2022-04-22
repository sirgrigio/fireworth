import { Injectable } from '@angular/core';
import { BalanceSheet, Item, ReferencePeriod, StatementSection } from '../statements.models';
import { DateTime } from 'luxon';

@Injectable({
  providedIn: 'root'
})
export class StatementsService {

  constructor() { }

  public getBalanceSheet(from: DateTime, to: DateTime, byQuarter: boolean): BalanceSheet {
    const subperiods = [];
    let cursor = from;
    while (cursor < to) {
      subperiods.push(cursor);
      cursor = cursor.plus({months: byQuarter ? 3 : 1});
    }
    return new BalanceSheet(
      new ReferencePeriod(
        subperiods,
        from.minus({months: byQuarter ? 3 : 1}).startOf(byQuarter ? 'quarter' : 'month'),
        to,
        byQuarter
      ),
      [
        new StatementSection(
          'CCE', 
          [new Item(0, 'Cash', 'EUR', [50, 50, 80, 20, 20, null, null, null, null, null, null, null], 50, 20)],
          [
            new StatementSection(
              'Savings Account',
              [new Item(0, 'Time Deposit', 'EUR', [1000, 1000, 1000, 1000, 1000, null, null, null, null, null, null, null], 1000, 1000)],
              [],
              new Item(0, 'Total', 'EUR', [1000, 1000, 1000, 1000, 1000, null, null, null, null, null, null, null], 1000, 1000)
            )
          ],
          new Item(0, 'Total', 'EUR', [1050, 1050, 1080, 1020, 1020, null, null, null, null, null, null, null], 1050, 1020)
        )
      ], 
      []
    );
  }
}

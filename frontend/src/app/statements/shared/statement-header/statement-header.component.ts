import { Component, Input, OnInit } from '@angular/core';
import { ReferencePeriod } from '../../statements.models';

@Component({
  selector: 'app-statement-header',
  templateUrl: './statement-header.component.html',
  styleUrls: ['./statement-header.component.scss']
})
export class StatementHeaderComponent implements OnInit {

  @Input() period?: ReferencePeriod;

  constructor() { }

  ngOnInit(): void {
  }

  fmtSubperiod(): string {
    if (this.period?.subperiods.length) {
      const first = this.period?.subperiods[0];
      const sameYear: boolean = this.period?.subperiods.every(
        e => e.hasSame(first, 'year')
      );
      if (this.period.byQuarter) {
        return sameYear ? "'Q'q" : "yyyy 'Q'q";
      } else {
        return sameYear ? 'MMM' : 'yyyy MMM';
      }
    }
    return 'MMM';
  }

  fmtStart(): string {
    return this.period?.byQuarter
      ? this.period.startsAtNewYear ? 'yyyy' : "yyyy 'Q'q"
      : this.period?.startsAtNewYear ? 'yyyy' 
      : this.period?.startsAtNewQuarter ? "yyyy 'Q'q" : 'yyyy MMM';
  }

  fmtEnd(): string {
    return this.period?.byQuarter
      ? this.period.endsAtNewYear ? 'yyyy' : "yyyy 'Q'q"
      : this.period?.endsAtNewYear ? 'yyyy' 
      : this.period?.endsAtNewQuarter? "yyyy 'Q'q" : 'yyyy MMM';
  }
}

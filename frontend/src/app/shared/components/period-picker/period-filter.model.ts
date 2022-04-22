import { DateTime } from 'luxon';

export class PeriodFilter {
    from: DateTime;
    to: DateTime;
    byQuarter: boolean

    constructor(from: DateTime, to: DateTime, byQuarter: boolean) {
        this.from = from;
        this.to = to;
        this.byQuarter = byQuarter;
    }
}
import { DateTime } from 'luxon';

export class Item {
    id: number;
    name: string;
    currency: string;
    values: (number | null)[];
    startValue: number | null;
    endValue: number | null;

    constructor(id: number, name: string, currency: string, values: (number | null)[], startValue: number | null, endValue: number | null) {
        this.id = id;
        this.name = name;
        this.currency = currency;
        this.values = values;
        this.startValue = startValue;
        this.endValue = endValue;
    }
}

export class StatementSection {
    title: string;
    items: Item[] = [];
    subsections: StatementSection[] = [];
    total: Item;

    constructor(title: string, items: Item[], subsections: StatementSection[], total: Item) {
        this.title = title;
        this.items = items;
        this.subsections = subsections;
        this.total = total;
    }
}

export class ReferencePeriod {
    subperiods: DateTime[];
    start: DateTime;
    end: DateTime;
    byQuarter: boolean;

    constructor(subperiods: DateTime[], start: DateTime, end: DateTime, byQuarter: boolean) {
        this.subperiods = subperiods;
        this.start = start;
        this.end = end;
        this.byQuarter = byQuarter;
    }

    get startsAtNewYear(): boolean {
        return this.subperiods[0].month == 1;
    }

    get startsAtNewQuarter(): boolean {
        return this.subperiods[0].month % 3 == 1;
    }

    get endsAtNewYear(): boolean {
        return this.end.month == 12;
    }

    get endsAtNewQuarter(): boolean {
        return this.end.month % 3 == 0;
    }
}

export class BalanceSheet {
    period: ReferencePeriod;
    assets: StatementSection[];
    liabilities: StatementSection[];

    constructor(period: ReferencePeriod, assets: StatementSection[], liabilities: StatementSection[]) {
        this.period = period;
        this.assets = assets;
        this.liabilities = liabilities;
    }
}
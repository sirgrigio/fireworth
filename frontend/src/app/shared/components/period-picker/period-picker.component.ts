import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { DateTime } from 'luxon';
import { BsDatepickerConfig, BsDatepickerViewMode } from 'ngx-bootstrap/datepicker';
import { PeriodFilter } from './period-filter.model';


type DefaultFilter = 'this_y' | 'this_q' | 'last_4q' | 'last_y' | 'last_3y' | 'custom';

@Component({
  selector: 'app-period-picker',
  templateUrl: './period-picker.component.html',
  styleUrls: ['./period-picker.component.scss']
})
export class PeriodPickerComponent implements OnInit {

  @Output() onPeriodFilterChange = new EventEmitter<PeriodFilter>();

  rangeValues?: (Date | undefined)[];
  bsConfig?: Partial<BsDatepickerConfig>;

  selectedFilter?: PeriodFilter;
  selectedDefaultFilterId?: DefaultFilter;
  defaultFilters: Map<string, PeriodFilter> = new Map<string, PeriodFilter>();

  constructor() { }

  ngOnInit(): void {
    this.bsConfig = Object.assign({}, {
      containerClass: 'theme-default',
      rangeInputFormat: 'MMM YYYY',
      isAnimated: true,
      minMode: <BsDatepickerViewMode>'month',
    });
    const now = DateTime.now();
    this.defaultFilters = new Map<DefaultFilter, PeriodFilter>([
      ['this_q', new PeriodFilter(now.startOf('quarter'), now.endOf('quarter'), false)],
      ['this_y', new PeriodFilter(now.startOf('year'), now.endOf('year'), false)],
      ['last_y', new PeriodFilter(
        now.minus({ years: 1 }).startOf('year'),
        now.minus({ years: 1 }).endOf('year'),
        false
      )],
      ['last_4q', new PeriodFilter(
        now.minus({ months: 12 }).startOf('quarter'),
        now.minus({ months: 3 }).endOf('quarter'),
        true
      )],
      ['last_3y', new PeriodFilter(
        now.minus({ years: 3 }).startOf('year'),
        now.minus({ years: 1 }).endOf('year'),
        true
      )],
    ]);
    if (!this.selectedFilter) {
      this.selectedFilter = this.defaultFilters.get('this_y');
      this.selectedDefaultFilterId = 'this_y';
      this.onPeriodFilterChange.emit(this.selectedFilter);
    }
  }

  onSelectedDefaultFilterChange(value: DefaultFilter) {
    this.selectedDefaultFilterId = value;
    this.selectedFilter = this.defaultFilters.get(value);
    this.onPeriodFilterChange.emit(this.selectedFilter);
  }

  onPickedRangeChange(values: (Date | undefined)[] | undefined) {
    this.rangeValues = values;
    if (values) {
      this.selectedFilter = new PeriodFilter(
        DateTime.fromJSDate(values[0] || new Date()).startOf('month'),
        DateTime.fromJSDate(values[1] || new Date()).endOf('month'),
        this.selectedFilter?.byQuarter || false
      );
      this.onPeriodFilterChange.emit(this.selectedFilter);
    }
  }

  onGroupByQuarterToggled(value: boolean) {
    if (this.selectedFilter) {
      this.selectedFilter = new PeriodFilter(
        this.selectedFilter.from,
        this.selectedFilter.to,
        value
      )
      this.onPeriodFilterChange.emit(this.selectedFilter);
    }
  }
}

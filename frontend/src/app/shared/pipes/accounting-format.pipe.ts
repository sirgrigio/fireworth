import { Pipe, PipeTransform } from '@angular/core';
import { RoundPipe } from 'ngx-pipes';

@Pipe({
  name: 'acct'
})
export class AccountingFormatPipe implements PipeTransform {

  transform(value: number | null, precision: number = 0, ...args: unknown[]): string {
    const rounded = this.round(value, precision);
    return rounded && rounded != 0 ?
      rounded > 0 ? rounded.toLocaleString('en-US') : `(${rounded.toLocaleString('en-US')})`
      : '\u2012';
  }

  private round(value: number | null, precision: number): number | boolean {
    if (value == null) {
      return false;
    }
    if (precision <= 0) {
      return Math.round(value);
    }
    const tho = 10 ** precision;
    return Math.round(value * tho) / tho;
  }
}

import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'csymbol'
})
export class CurrencySymbolPipe implements PipeTransform {

  transform(value: string, ...args: unknown[]): string {
    return (0).toLocaleString(
      'en-US', {
        style: 'currency',
        currency: value,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }
    ).replace(/\d/g, '').trim()
  }

}

import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { CellComponent } from './components/cell/cell.component';
import { AccountingFormatPipe } from './pipes/accounting-format.pipe';
import { CurrencySymbolPipe } from './pipes/currency-symbol.pipe';
import { PeriodPickerComponent } from './components/period-picker/period-picker.component';
import { BsDatepickerModule } from 'ngx-bootstrap/datepicker';
import { ButtonsModule } from 'ngx-bootstrap/buttons';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';



@NgModule({
  declarations: [
    CellComponent,
    CurrencySymbolPipe,
    AccountingFormatPipe,
    PeriodPickerComponent
  ],
  imports: [
    CommonModule,
    BsDatepickerModule.forRoot(),
    ButtonsModule.forRoot(),
    FormsModule,
    TranslateModule.forChild(),
  ],
  exports: [
    AccountingFormatPipe,
    CellComponent,
    CurrencySymbolPipe,
    PeriodPickerComponent
  ]
})
export class SharedModule { }

import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { LuxonModule } from 'luxon-angular';
import { BsDatepickerModule } from 'ngx-bootstrap/datepicker';
import { BsDropdownModule } from 'ngx-bootstrap/dropdown';
import { TypeaheadModule } from 'ngx-bootstrap/typeahead';
import { SharedModule } from '../shared/shared.module';
import { LedgerRoutingModule } from './ledger-routing.module';
import { LedgerComponent } from './ledger.component';
import { TransactionFilterComponent } from './transaction-filter/transaction-filter.component';
import { TransactionSmartInputComponent } from './transaction-smart-input/transaction-smart-input.component';
import { TransactionsComponent } from './transactions/transactions.component';
import { TxnEditDateComponent } from './transactions/txn-edit-date/txn-edit-date.component';
import { TxnEditAccountComponent } from './transactions/txn-edit-account/txn-edit-account.component';
import { TxnEditCategoryComponent } from './transactions/txn-edit-category/txn-edit-category.component';
import { TxnEditPayeeComponent } from './transactions/txn-edit-payee/txn-edit-payee.component';
import { TxnEditMemoComponent } from './transactions/txn-edit-memo/txn-edit-memo.component';
import { TxnEditAmountComponent } from './transactions/txn-edit-amount/txn-edit-amount.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';


@NgModule({
  declarations: [
    LedgerComponent,
    TransactionSmartInputComponent,
    TransactionFilterComponent,
    TransactionsComponent,
    TxnEditDateComponent,
    TxnEditAccountComponent,
    TxnEditCategoryComponent,
    TxnEditPayeeComponent,
    TxnEditMemoComponent,
    TxnEditAmountComponent,
  ],
  imports: [
    CommonModule,
    LedgerRoutingModule,
    TranslateModule.forChild(),
    SharedModule,
    NgxDatatableModule,
    LuxonModule,
    FormsModule,
    BsDatepickerModule.forRoot(),
    BsDropdownModule.forRoot(),
    TypeaheadModule.forRoot(),
    FontAwesomeModule,
  ]
})
export class LedgerModule { }

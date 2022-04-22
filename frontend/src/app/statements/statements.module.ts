import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { CollapseModule } from 'ngx-bootstrap/collapse';
import { NgPipesModule } from 'ngx-pipes';
import { SharedModule } from '../shared/shared.module';
import { BalanceSheetComponent } from './balance-sheet/balance-sheet.component';
import { CashFlowStatementComponent } from './cash-flow-statement/cash-flow-statement.component';
import { IncomeStatementComponent } from './income-statement/income-statement.component';
import { StatementSectionComponent } from './shared/statement-section/statement-section.component';
import { StatementsRoutingModule } from './statements-routing.module';
import { StatementsComponent } from './statements.component';
import { StatementHeaderComponent } from './shared/statement-header/statement-header.component';
import { LuxonModule } from 'luxon-angular';


@NgModule({
  declarations: [
    IncomeStatementComponent,
    CashFlowStatementComponent,
    BalanceSheetComponent,
    StatementSectionComponent,
    StatementsComponent,
    StatementHeaderComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    StatementsRoutingModule,
    NgPipesModule,
    CollapseModule,
    FontAwesomeModule,
    TranslateModule.forChild(),
    LuxonModule,
  ]
})
export class StatementsModule { }

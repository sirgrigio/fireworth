import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CashFlowStatementComponent } from './cash-flow-statement.component';

describe('CashFlowStatementComponent', () => {
  let component: CashFlowStatementComponent;
  let fixture: ComponentFixture<CashFlowStatementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CashFlowStatementComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CashFlowStatementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

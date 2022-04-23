import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TxnEditAmountComponent } from './txn-edit-amount.component';

describe('TxnEditAmountComponent', () => {
  let component: TxnEditAmountComponent;
  let fixture: ComponentFixture<TxnEditAmountComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TxnEditAmountComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TxnEditAmountComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

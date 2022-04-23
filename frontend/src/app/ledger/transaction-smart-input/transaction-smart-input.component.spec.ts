import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransactionSmartInputComponent } from './transaction-smart-input.component';

describe('TransactionInputComponent', () => {
  let component: TransactionSmartInputComponent;
  let fixture: ComponentFixture<TransactionSmartInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TransactionSmartInputComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TransactionSmartInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

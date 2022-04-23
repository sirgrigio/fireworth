import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TxnEditAccountComponent } from './txn-edit-account.component';

describe('TxnEditAccountComponent', () => {
  let component: TxnEditAccountComponent;
  let fixture: ComponentFixture<TxnEditAccountComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TxnEditAccountComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TxnEditAccountComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

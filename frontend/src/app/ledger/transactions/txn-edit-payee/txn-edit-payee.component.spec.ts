import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TxnEditPayeeComponent } from './txn-edit-payee.component';

describe('TxnEditPayeeComponent', () => {
  let component: TxnEditPayeeComponent;
  let fixture: ComponentFixture<TxnEditPayeeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TxnEditPayeeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TxnEditPayeeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

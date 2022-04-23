import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TxnEditDateComponent } from './txn-edit-date.component';

describe('TxnEditDateComponent', () => {
  let component: TxnEditDateComponent;
  let fixture: ComponentFixture<TxnEditDateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TxnEditDateComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TxnEditDateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

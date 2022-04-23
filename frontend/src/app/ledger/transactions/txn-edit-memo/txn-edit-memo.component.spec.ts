import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TxnEditMemoComponent } from './txn-edit-memo.component';

describe('TxnEditMemoComponent', () => {
  let component: TxnEditMemoComponent;
  let fixture: ComponentFixture<TxnEditMemoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TxnEditMemoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TxnEditMemoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

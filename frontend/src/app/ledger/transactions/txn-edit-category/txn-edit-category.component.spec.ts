import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TxnEditCategoryComponent } from './txn-edit-category.component';

describe('TxnEditCategoryComponent', () => {
  let component: TxnEditCategoryComponent;
  let fixture: ComponentFixture<TxnEditCategoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TxnEditCategoryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TxnEditCategoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

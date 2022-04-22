import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatementHeaderComponent } from './statement-header.component';

describe('StatementHeaderComponent', () => {
  let component: StatementHeaderComponent;
  let fixture: ComponentFixture<StatementHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ StatementHeaderComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StatementHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

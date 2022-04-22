import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatementSectionComponent } from './statement-section.component';

describe('StatementSectionComponent', () => {
  let component: StatementSectionComponent;
  let fixture: ComponentFixture<StatementSectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ StatementSectionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StatementSectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

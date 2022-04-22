import { TestBed } from '@angular/core/testing';

import { StatementsService } from './statements.service';

describe('StatementsService', () => {
  let service: StatementsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StatementsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

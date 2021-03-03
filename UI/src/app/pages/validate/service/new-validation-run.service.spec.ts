import {TestBed} from '@angular/core/testing';

import {NewValidationRunService} from './new-validation-run.service';

describe('NewValidationRunService', () => {
  let service: NewValidationRunService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NewValidationRunService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

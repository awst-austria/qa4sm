import {TestBed} from '@angular/core/testing';

import {ValidationRunConfigService} from './validation-run-config.service';

describe('NewValidationRunService', () => {
  let service: ValidationRunConfigService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ValidationRunConfigService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

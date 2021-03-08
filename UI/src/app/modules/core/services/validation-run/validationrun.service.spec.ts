import {TestBed} from '@angular/core/testing';

import {ValidationrunService} from './validationrun.service';

describe('ValidationrunService', () => {
  let service: ValidationrunService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ValidationrunService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

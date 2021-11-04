import {TestBed} from '@angular/core/testing';

import {ValidationrunResolver} from './validationrun.resolver';
import {ValidationrunService} from '../../../modules/core/services/validation-run/validationrun.service';

describe('ValidationrunResolver', () => {
  let resolver: ValidationrunResolver;
  const validationServiceSpy = jasmine.createSpyObj('ValidationrunService',
    ['getValidationRunById']);

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{provide: ValidationrunService, useValue: validationServiceSpy}]
    });
    resolver = TestBed.inject(ValidationrunResolver);
  });

  it('should be created', () => {
    expect(resolver).toBeTruthy();
  });
});

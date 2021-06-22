import {TestBed} from '@angular/core/testing';

import {ValidationrunResolver} from './validationrun.resolver';

describe('ValidationrunResolver', () => {
  let resolver: ValidationrunResolver;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    resolver = TestBed.inject(ValidationrunResolver);
  });

  it('should be created', () => {
    expect(resolver).toBeTruthy();
  });
});

import {TestBed} from '@angular/core/testing';

import {DatasetResolver} from './dataset.resolver';

describe('DatasetResolver', () => {
  let resolver: DatasetResolver;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    resolver = TestBed.inject(DatasetResolver);
  });

  it('should be created', () => {
    expect(resolver).toBeTruthy();
  });
});

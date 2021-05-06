import {TestBed} from '@angular/core/testing';

import {DatasetConfigurationResolver} from './dataset-configuration.resolver';

describe('DatasetConfigurationResolver', () => {
  let resolver: DatasetConfigurationResolver;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    resolver = TestBed.inject(DatasetConfigurationResolver);
  });

  it('should be created', () => {
    expect(resolver).toBeTruthy();
  });
});

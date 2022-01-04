import { TestBed } from '@angular/core/testing';

import { DatasetConfigurationService } from './dataset-configuration.service';

describe('DatasetConfigurationService', () => {
  let service: DatasetConfigurationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DatasetConfigurationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

import {TestBed} from '@angular/core/testing';

import {DatasetVersionService} from './dataset-version.service';

describe('DatasetVersionService', () => {
  let service: DatasetVersionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DatasetVersionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

import {TestBed} from '@angular/core/testing';

import {DatasetVariableService} from './dataset-variable.service';

describe('DatasetVariavleService', () => {
  let service: DatasetVariableService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DatasetVariableService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

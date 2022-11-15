import {TestBed} from '@angular/core/testing';

import {UserDatasetsService} from './user-datasets.service';

describe('UserDatasetsService', () => {
  let service: UserDatasetsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserDatasetsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

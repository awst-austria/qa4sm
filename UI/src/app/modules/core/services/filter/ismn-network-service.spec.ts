import {TestBed} from '@angular/core/testing';

import {IsmnNetworkService} from './ismn-network-service';

describe('IsmnNetworkService', () => {
  let service: IsmnNetworkService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(IsmnNetworkService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

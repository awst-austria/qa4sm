import {TestBed} from '@angular/core/testing';

import {IsmnNetworkServiceService} from './ismn-network-service.service';

describe('IsmnNetworkServiceService', () => {
  let service: IsmnNetworkServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(IsmnNetworkServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

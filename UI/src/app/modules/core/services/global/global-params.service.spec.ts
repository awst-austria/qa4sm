import { TestBed } from '@angular/core/testing';

import { GlobalParamsService } from './global-params.service';

describe('GlobalParamsService', () => {
  let service: GlobalParamsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GlobalParamsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

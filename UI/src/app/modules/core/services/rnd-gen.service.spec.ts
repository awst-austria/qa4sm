import { TestBed } from '@angular/core/testing';

import { RndGenService } from './rnd-gen.service';

describe('RndGenService', () => {
  let service: RndGenService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RndGenService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

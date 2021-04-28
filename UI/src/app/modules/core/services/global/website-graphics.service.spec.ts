import {TestBed} from '@angular/core/testing';

import {WebsiteGraphicsService} from './website-graphics.service';

describe('WebsiteGraphicsService', () => {
  let service: WebsiteGraphicsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(WebsiteGraphicsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

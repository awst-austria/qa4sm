import {TestBed} from '@angular/core/testing';

import {DatasetConfigurationService} from './dataset-configuration.service';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';

describe('DatasetConfigurationService', () => {
  let service: DatasetConfigurationService;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({imports: [HttpClientTestingModule]});
    service = TestBed.inject(DatasetConfigurationService);
    httpClient = TestBed.inject(HttpClient);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

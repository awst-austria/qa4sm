import {HttpTestingController, provideHttpClientTesting} from '@angular/common/http/testing';
import {HttpClient, provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import {TestBed} from '@angular/core/testing';

import {DatasetVariableService} from './dataset-variable.service';

describe('DatasetVariavleService', () => {
  let service: DatasetVariableService;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [], providers: [provideHttpClient(withInterceptorsFromDi()), provideHttpClientTesting()] });
    service = TestBed.inject(DatasetVariableService);
    httpClient = TestBed.inject(HttpClient);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

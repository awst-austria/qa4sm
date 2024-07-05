import {HttpTestingController, provideHttpClientTesting} from '@angular/common/http/testing';
import {HttpClient, provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import {TestBed} from '@angular/core/testing';

import {LocalApiService} from './local-api.service';

describe('LocalApiService', () => {
  let service: LocalApiService;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [], providers: [provideHttpClient(withInterceptorsFromDi()), provideHttpClientTesting()] });
    service = TestBed.inject(LocalApiService);
    httpClient = TestBed.inject(HttpClient);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

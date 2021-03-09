import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ValidationrunDto} from './validationrun.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';

const publishedValidationRunUrl: string = environment.API_URL + 'api/published-results';
const customValidationRunUrl: string = environment.API_URL + 'api/my-results';
const validationRunsUrl: string = environment.API_URL + 'api/validation-runs';

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {

  customValidationrun$: Observable<ValidationrunDto[]>;
  publishedValidationrun$: Observable<ValidationrunDto[]>;

  constructor(private httpClient: HttpClient) {
    this.publishedValidationrun$ = this.httpClient.get<ValidationrunDto[]>(publishedValidationRunUrl);
    this.customValidationrun$ = this.httpClient.get<ValidationrunDto[]>(customValidationRunUrl);
  }

  getPublishedValidationruns(): Observable<ValidationrunDto[]> {
    this.publishedValidationrun$ = this.httpClient.get<ValidationrunDto[]>(publishedValidationRunUrl);
    return this.publishedValidationrun$;
  }

  getMyValidationruns(): Observable<ValidationrunDto[]> {
    this.customValidationrun$ = this.httpClient.get<ValidationrunDto[]>(customValidationRunUrl);
    return this.customValidationrun$;
  }

  getValidationRuns(): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(validationRunsUrl);
  }

  getValidationRunById(id: string): Observable<ValidationrunDto> {
    return this.httpClient.get<ValidationrunDto>(`${validationRunsUrl}/${id}`);
  }
}

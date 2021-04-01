import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {ValidationrunDto} from './validationrun.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {ValidationSetDto} from '../../../validation-result/services/validation.set.dto';

const publishedValidationRunUrl: string = environment.API_URL + 'api/published-results';
const customValidationRunUrl: string = environment.API_URL + 'api/my-results';
const validationRunsUrl: string = environment.API_URL + 'api/validation-runs';

const csrfToken = '{{csrf_token}}';
const resultUrl =  environment.API_URL + 'api/modify-validation/00000000-0000-0000-0000-000000000000';
const stopValidationUrl = environment.API_URL + 'api/stop-validation/00000000-0000-0000-0000-000000000000';

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {

  customValidationrun$: Observable<ValidationSetDto>;
  publishedValidationrun$: Observable<ValidationSetDto>;

  constructor(private httpClient: HttpClient) {
  }

  getPublishedValidationruns(params: any): Observable<ValidationSetDto>{
    this.publishedValidationrun$ = this.httpClient.get<ValidationSetDto>(publishedValidationRunUrl, {params});
    return  this.publishedValidationrun$;
  }

  getMyValidationruns(params: any): Observable<ValidationSetDto>{
    this.customValidationrun$ = this.httpClient.get<ValidationSetDto>(customValidationRunUrl, {params});
    return  this.customValidationrun$;
  }

  getValidationRuns(): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(validationRunsUrl);
  }

  getValidationRunById(id: string): Observable<ValidationrunDto> {
    return this.httpClient.get<ValidationrunDto>(`${validationRunsUrl}/${id}`);
  }

  deleteValidation(validationId: string): void{
    if (!confirm('Do you really want to delete the result?')) {
      return;
    }
    const deleteUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const headers = new HttpHeaders({'X-CSRFToken': csrfToken});
    this.httpClient.delete(deleteUrl, {headers}).subscribe(
      () => {
        console.log('done');
      }
    );
  }



}

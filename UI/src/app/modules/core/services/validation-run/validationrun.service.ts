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
const resultUrl = environment.API_URL + 'api/modify-validation/00000000-0000-0000-0000-000000000000';
const stopValidationUrl = environment.API_URL + 'api/stop-validation/00000000-0000-0000-0000-000000000000';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {

  customValidationrun$: Observable<ValidationSetDto>;
  publishedValidationrun$: Observable<ValidationSetDto>;

  constructor(private httpClient: HttpClient) {
  }

  getPublishedValidationruns(params: any): Observable<ValidationSetDto> {
    this.publishedValidationrun$ = this.httpClient.get<ValidationSetDto>(publishedValidationRunUrl, {params});
    return this.publishedValidationrun$;
  }

  getMyValidationruns(params: any): Observable<ValidationSetDto> {
    this.customValidationrun$ = this.httpClient.get<ValidationSetDto>(customValidationRunUrl, {params});
    return this.customValidationrun$;
  }

  getValidationRuns(): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(validationRunsUrl);
  }

  getValidationRunById(id: string): Observable<ValidationrunDto> {
    return this.httpClient.get<ValidationrunDto>(`${validationRunsUrl}/${id}`);
  }

  deleteValidation(validationId: string): void {
    if (!confirm('Do you really want to delete the result?')) {
      return;
    }
    const deleteUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    this.httpClient.delete(deleteUrl, {headers}).subscribe(
      () => {
      });
  }

  stopValidation(validationId: string): void {
    if (!confirm('Do you really want to stop the validation?')) {
      return;
    }
    const stopUrl = stopValidationUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    this.httpClient.delete(stopUrl, {headers}).subscribe(
      () => {
      });
  }

  archiveResults(validationId: string, archive: boolean): void {
    if (!confirm('Do you want to ' + (archive ? 'archive' : 'un-archive')
      + ' the result' + (archive ? '' : ' (allow auto-cleanup)') + '?')) {
      return;
    }
    const archiveUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    this.httpClient.patch(archiveUrl + '/', {archive}, {headers, observe: 'response', responseType: 'text'}).subscribe(
      () => {
      });
  }

  extendResults(validationId: string): void {
    if (!confirm('Do you want to extend the lifespan of this result?')) {
      return;
    }
    const extendUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const extend = true;
    this.httpClient.patch(extendUrl + '/', {extend}, {headers, observe: 'body', responseType: 'text'}).subscribe(
      (response) => {
        const newExpiry = new Date(response);
        alert('The expiry date of your validation has been shifted to ' + newExpiry.toLocaleDateString());
      });
  }

  saveResults(validationId: string, newName: string): void {
    const saveUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {save_name: true, new_name: newName};
    console.log(data);
    this.httpClient.patch(saveUrl + '/', data, {headers , observe: 'body', responseType: 'json'}).subscribe(
      () => {
      });

  }
}

import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {ValidationrunDto} from './validationrun.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {ValidationSetDto} from '../../../validation-result/services/validation.set.dto';
import {saveAs} from 'file-saver-es';
import {MetricsPlotsDto} from './metrics-plots.dto';
import {DataCache} from '../../tools/DataCache';
import {shareReplay} from 'rxjs/operators';
import {HttpParamsModel} from './http-params.model';

const urlPrefix = environment.API_URL + 'api';
const publishedValidationRunUrl: string = urlPrefix + '/published-results';
const customValidationRunUrl: string = urlPrefix + '/my-results';
const validationRunsUrl: string = urlPrefix + '/validation-runs';
const trackedCustomRunsUrl: string = urlPrefix + '/custom-tracked-run';
const downloadResultsUrl: string = urlPrefix + '/download-result';
const summaryStatisticsUrl: string = urlPrefix + '/summary-statistics';
const downloadStatisticsCsvUrl: string = urlPrefix + '/download-statistics-csv';
const metricsAndPlotsNamesUrl: string = urlPrefix + '/get-metric-and-plots-names';
// const downloadResultsGraphsUrl: string = urlPrefix + '/get-graphic-file';

const csrfToken = '{{csrf_token}}';
const resultUrl = urlPrefix + '/modify-validation/00000000-0000-0000-0000-000000000000';
const stopValidationUrl = urlPrefix + '/stop-validation/00000000-0000-0000-0000-000000000000';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});
const CACHE_KEY_ALL_PUBLISHED_VALIDATIONS = -1;
const CACHE_KEY_PUBLISHED_VALIDATIONS_PARAMS = -1;

const CACHE_KEY_ALL_CUSTOM_VALIDATIONS = -1;
const CACHE_KEY_CUSTOM_VALIDATIONS_PARAMS = -1;

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {

  // cache for validation arrays
  publishedValidationsRequestCache = new DataCache<Observable<ValidationSetDto>>(5);
  publishedValidationsParameters = new DataCache<HttpParamsModel>(5);

  customValidationsRequestCache = new DataCache<Observable<ValidationSetDto>>(5);
  customValidationsParameters = new DataCache<HttpParamsModel>(5);

  singleValidationRequestCache = new DataCache<Observable<ValidationrunDto>>(5);

  constructor(private httpClient: HttpClient) {
  }

  private compareTwoModels(instanceOne: any, instanceTwo: any): boolean {
    // function for comparing two instances of the same model
    return JSON.stringify(instanceOne) === JSON.stringify(instanceTwo);
  }

  getPublishedValidationruns(parameters: HttpParamsModel): Observable<ValidationSetDto> {
    if (this.publishedValidationsRequestCache.isCached(CACHE_KEY_ALL_PUBLISHED_VALIDATIONS) &&
      this.compareTwoModels(parameters, this.publishedValidationsParameters.get(CACHE_KEY_PUBLISHED_VALIDATIONS_PARAMS))) {
      return this.publishedValidationsRequestCache.get(CACHE_KEY_ALL_PUBLISHED_VALIDATIONS);
    } else {
      const params = new HttpParams().set('offset', String(parameters.offset)).set('limit', String(parameters.limit))
        .set('order', String(parameters.order));
      const validations$ = this.httpClient.get<ValidationSetDto>(publishedValidationRunUrl, {params}).pipe(shareReplay());
      this.publishedValidationsRequestCache.push(CACHE_KEY_ALL_PUBLISHED_VALIDATIONS, validations$);
      this.publishedValidationsParameters.push(CACHE_KEY_PUBLISHED_VALIDATIONS_PARAMS, parameters);
      return validations$;
    }
  }

  getMyValidationruns(parameters: HttpParamsModel): Observable<ValidationSetDto> {
    if (this.customValidationsRequestCache.isCached(CACHE_KEY_ALL_CUSTOM_VALIDATIONS) &&
      this.compareTwoModels(parameters, this.customValidationsParameters.get(CACHE_KEY_CUSTOM_VALIDATIONS_PARAMS))) {
      return this.customValidationsRequestCache.get(CACHE_KEY_ALL_CUSTOM_VALIDATIONS);
    } else {
      const params = new HttpParams().set('offset', String(parameters.offset)).set('limit', String(parameters.limit))
        .set('order', String(parameters.order));
      const validations$ = this.httpClient.get<ValidationSetDto>(customValidationRunUrl, {params}).pipe(shareReplay());
      this.customValidationsRequestCache.push(CACHE_KEY_ALL_CUSTOM_VALIDATIONS, validations$);
      this.customValidationsParameters.push(CACHE_KEY_CUSTOM_VALIDATIONS_PARAMS, parameters);
      return validations$;
    }
  }

  getValidationRuns(): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(validationRunsUrl);
  }

  getValidationRunById(id: string): Observable<ValidationrunDto> {
    // return this.httpClient.get<ValidationrunDto>(`${validationRunsUrl}/${id}`);
    if (this.singleValidationRequestCache.isCached(id)) {
      return this.singleValidationRequestCache.get(id);
    } else {
      const getURL = validationRunsUrl + '/' + id;
      const validationrun$ = this.httpClient.get<ValidationrunDto>(getURL).pipe(shareReplay());
      this.singleValidationRequestCache.push(id, validationrun$);
      return validationrun$;
    }


  }

  getCustomTrackedValidations(): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(trackedCustomRunsUrl);
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
        location.reload();
      });
  }

  saveResults(validationId: string, newName: string): void {
    const saveUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {save_name: true, new_name: newName};
    console.log(data);
    this.httpClient.patch(saveUrl + '/', data, {headers, observe: 'body', responseType: 'json'}).subscribe(
      () => {
      });

  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    const fileUrl = `${downloadResultsUrl}?validationId=${validationId}&fileType=${fileType}`;
    saveAs(fileUrl, fileName);
  }

  addValidation(validationId: string): void {
    const addUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {add_validation: true};
    this.httpClient.post(addUrl + '/', data, {headers, observe: 'body', responseType: 'text'}).subscribe(
      response => {
        alert(response);
      }
    );
  }

  removeValidation(validationId: string): void {
    if (!confirm('Do you really want to remove this validation from your list?')) {
      return;
    }
    const addUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {remove_validation: true};
    this.httpClient.post(addUrl + '/', data, {headers, observe: 'body', responseType: 'text'}).subscribe(
      response => alert(response)
    );
  }

  getSummaryStatistics(params: any): Observable<any> {
    return this.httpClient.get(summaryStatisticsUrl, {params, headers, responseType: 'text'});
  }

  downloadSummaryStatisticsCsv(validationId: string): void {
    const fileUrl = `${downloadStatisticsCsvUrl}?validationId=${validationId}`;
    saveAs(fileUrl);
  }

  getMetricsAndPlotsNames(params: any): Observable<MetricsPlotsDto[]> {
    return this.httpClient.get<MetricsPlotsDto[]>(metricsAndPlotsNamesUrl, {params});
  }

}

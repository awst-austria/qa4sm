import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {ValidationrunDto} from './validationrun.dto';
import {BehaviorSubject, Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {ValidationSetDto} from '../../../validation-result/services/validation.set.dto';
import {saveAs} from 'file-saver-es';
import {MetricsPlotsDto} from './metrics-plots.dto';
import {PublishingFormDto} from './publishing-form.dto';
import {HttpErrorService} from '../global/http-error.service';
import {catchError} from 'rxjs/operators';

const urlPrefix = environment.API_URL + 'api';
const publishedValidationRunUrl: string = urlPrefix + '/published-results';
const customValidationRunUrl: string = urlPrefix + '/my-results';
const validationRunsUrl: string = urlPrefix + '/validation-runs';
const trackedCustomRunsUrl: string = urlPrefix + '/custom-tracked-run';
const downloadResultsUrl: string = urlPrefix + '/download-result';
const summaryStatisticsUrl: string = urlPrefix + '/summary-statistics';
const downloadStatisticsCsvUrl: string = urlPrefix + '/download-statistics-csv';
const metricsAndPlotsNamesUrl: string = urlPrefix + '/get-metric-and-plots-names';
const validations4ComparisonUrl: string = urlPrefix + '/validation-runs-for-comparison';
const publishingFormURL: string = urlPrefix + '/publishing-form';
const copyValidationUrl: string = urlPrefix + '/copy-validation';
const copiedValidationRecordUrl: string = urlPrefix + '/copied-validation-record';


const csrfToken = '{{csrf_token}}';
const changeNameUrl = urlPrefix + '/change-validation-name/00000000-0000-0000-0000-000000000000';
const archiveResultUrl = urlPrefix + '/archive-result/00000000-0000-0000-0000-000000000000';
const extendResultUrl = urlPrefix + '/extend-result/00000000-0000-0000-0000-000000000000';
const publishResultUrl = urlPrefix + '/publish-result/00000000-0000-0000-0000-000000000000';
const addValidationUrl = urlPrefix + '/add-validation/00000000-0000-0000-0000-000000000000';
const removeValidationUrl = urlPrefix + '/remove-validation/00000000-0000-0000-0000-000000000000';
const removeMultipleValidationUrl = urlPrefix + '/delete-multiple-validations';
const archiveMultipleValidationUrl = urlPrefix + '/archive-multiple-validations';
const deleteResultUrl = urlPrefix + '/delete-validation/00000000-0000-0000-0000-000000000000';
const stopValidationUrl = urlPrefix + '/stop-validation/00000000-0000-0000-0000-000000000000';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {
  private refresh: BehaviorSubject<string> = new BehaviorSubject('');

  doRefresh = this.refresh.asObservable();
  customValidationrun$: Observable<ValidationSetDto>;
  publishedValidationrun$: Observable<ValidationSetDto>;

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
  }

  getPublishedValidationruns(params: any): Observable<ValidationSetDto> {
    return this.httpClient.get<ValidationSetDto>(publishedValidationRunUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getMyValidationruns(params: any): Observable<ValidationSetDto> {
    return this.httpClient.get<ValidationSetDto>(customValidationRunUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getValidationRunById(id: string): Observable<ValidationrunDto> {
    return this.httpClient.get<ValidationrunDto>(`${validationRunsUrl}/${id}`)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getCustomTrackedValidations(): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(trackedCustomRunsUrl)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getValidationsForComparison(params: any): Observable<ValidationrunDto[]> {
    return this.httpClient.get<ValidationrunDto[]>(validations4ComparisonUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  deleteValidation(validationId: string): Observable<any> {
    const deleteUrl = deleteResultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    return this.httpClient.delete(deleteUrl, {headers})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  stopValidation(validationId: string): Observable<any> {
    const stopUrl = stopValidationUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    return this.httpClient.delete(stopUrl, {headers})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  archiveResult(validationId: string, archive: boolean): Observable<any> {
    const archiveUrl = archiveResultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    return this.httpClient.patch(archiveUrl + '/', {archive},
      {headers, observe: 'response', responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  extendResult(validationId: string): Observable<any> {
    const extendUrl = extendResultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const extend = true;
    return this.httpClient.patch(extendUrl + '/', {extend},
      {headers, observe: 'response', responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  saveResultsName(validationId: string, newName: string): Observable<any> {
    const saveUrl = changeNameUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {save_name: true, new_name: newName};
    return this.httpClient.patch(saveUrl + '/', data, {headers, observe: 'body', responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );

  }

  publishResults(validationId: string, publishingData: any): Observable<any> {
    const publishUrl = publishResultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {publish: true, publishing_form: publishingData};
    return this.httpClient.patch(publishUrl + '/', data, {headers, observe: 'body', responseType: 'json'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    const fileUrl = `${downloadResultsUrl}?validationId=${validationId}&fileType=${fileType}`;
    saveAs(fileUrl, fileName);
  }

  addValidation(validationId: string): Observable<any> {
    const addUrl = addValidationUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {add_validation: true};
    return this.httpClient.post(addUrl + '/', data, {headers, observe: 'body', responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  removeValidation(validationId: string): Observable<any> {
    const addUrl = removeValidationUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
    const data = {remove_validation: true};
    return this.httpClient.post(addUrl + '/', data, {headers, observe: 'body', responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  removeMultipleValidation(validationId: string[]): Observable<any> {
    let params = new HttpParams();
    validationId.forEach(id => {params = params.append('id', id);})
    return this.httpClient.delete(removeMultipleValidationUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  archiveMultipleValidation(validationId: string[], archive): Observable<any> {
    let params = new HttpParams().set('archive', archive);
    validationId.forEach(id => {
      params = params.append('id', id);
    })

    return this.httpClient.post(archiveMultipleValidationUrl, {},
      {headers, observe: 'body', params: params, responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getSummaryStatistics(params: any): Observable<any> {
    return this.httpClient.get(summaryStatisticsUrl, {params, headers, responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  downloadSummaryStatisticsCsv(validationId: string): void {
    const fileUrl = `${downloadStatisticsCsvUrl}?validationId=${validationId}`;
    saveAs(fileUrl);
  }

  getMetricsAndPlotsNames(params: any): Observable<MetricsPlotsDto[]> {
    return this.httpClient.get<MetricsPlotsDto[]>(metricsAndPlotsNamesUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getPublishingFormData(params: any): Observable<PublishingFormDto> {
    return this.httpClient.get<PublishingFormDto>(publishingFormURL, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  refreshComponent(validationIdOrPage: string): void {
    // here we can give or validation id or the word 'page' if entire page should be reloaded (e.g. when a validation is removed)
    this.refresh.next(validationIdOrPage);
  }

  copyValidation(params: any): Observable<any> {
    return this.httpClient.get(copyValidationUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getCopiedRunRecord(validationId: string): Observable<any> {
    const urlWithParam = copiedValidationRecordUrl + '/' + validationId;
    return this.httpClient.get(urlWithParam)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

}

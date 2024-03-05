import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {BehaviorSubject, Observable} from 'rxjs';
import {ValidationrunDto} from '../../core/services/validation-run/validationrun.dto';
import {MetricsComparisonDto} from './metrics-comparison.dto';
import {Validations2CompareModel} from '../components/validation-selector/validation-selection.model';
import {ExtentModel} from '../components/spatial-extent/extent-model';
import {PlotDto} from '../../core/services/global/plot.dto';
import {saveAs} from 'file-saver-es';
import {catchError} from 'rxjs/operators';
import {HttpErrorService} from '../../core/services/global/http-error.service';

const urlPrefix = environment.API_URL + 'api';
const comparisonPlotsUrl: string = urlPrefix + '/plots-comparison';
const comparisonTableUrl: string = urlPrefix + '/table-comparison';
const downloadComparisonTableUrl: string = urlPrefix + '/download-comparison-table';
const metrics4ComparisonUrl: string = urlPrefix + '/metrics-for-comparison';
const comparisonExtentImageUrl: string = urlPrefix + '/image-comparison';

const csrfToken = '{{csrf_token}}';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});

@Injectable({
  providedIn: 'root'
})
export class ComparisonService {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [],
    new ExtentModel(true).getIntersection,
    false
  );
  private comparisonModelSubject = new BehaviorSubject<Validations2CompareModel>(this.comparisonModel);
  currentComparisonModel = this.comparisonModelSubject.asObservable();

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
  }

  sendComparisonModel(newModel: Validations2CompareModel): void{
    this.comparisonModelSubject.next(newModel);
  }

  getValidationsIds(validations: ValidationrunDto[]): string[] {
    // get the ids of the validations
    const ids = [];
    for (const validation of validations){
      ids.push(validation.id);
    }
    return ids;
  }

  getMetrics4Comparison(params: any): Observable<MetricsComparisonDto[]> {
    // return all the metrics for the comparison configuration
    return this.httpClient.get<MetricsComparisonDto[]>(metrics4ComparisonUrl, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  getComparisonTable(params: any): Observable<any> {
    // create htm table in comparison page
    return this.httpClient.get(comparisonTableUrl, {params, headers, responseType: 'text'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  downloadComparisonTableCsv(ids: string[], metricList: string[], getIntersection: boolean, extent: string): void {
    // download comparison table
    let params = '?';
    ids.forEach(id => {
      params += `ids=${id}&`;
    });
    metricList.forEach(metric => {
      params += `metric_list=${metric}&`;
    });
    params += `get_intersection=${String(getIntersection)}`;
    // for now I leave here if because I don't know where the param comes from and we can not pass null, because python
    // treats it as an actual value
    if (extent){
      params += `&extent=${extent}`;
    }
    const fileUrl = `${downloadComparisonTableUrl}${params}`;
    saveAs(fileUrl);
  }

  getComparisonPlots(params: any): Observable<PlotDto[]> {
    return this.httpClient.get<PlotDto[]>(comparisonPlotsUrl, {params})
      .pipe(catchError(err => this.httpError.handleError(err)));
  }

  getComparisonExtentImage(params: any): Observable<string> {
    return this.httpClient.get<string>(comparisonExtentImageUrl, {params})
      .pipe(catchError(err => this.httpError.handleError(err)));
  }
}

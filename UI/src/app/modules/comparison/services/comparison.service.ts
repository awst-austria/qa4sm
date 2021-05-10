import {Injectable} from '@angular/core';
import {environment} from "../../../../environments/environment";
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {Observable} from "rxjs";
import {ValidationrunDto} from "../../core/services/validation-run/validationrun.dto";
import {MetricsComparisonDto} from "./metrics-comparison.dto";

const urlPrefix = environment.API_URL + 'api';
const comparisonPlotsUrl: string = urlPrefix + '/plots-comparison';
const comparisonTableUrl: string = urlPrefix + '/table-comparison';
const downloadComparisonTableUrl: string = urlPrefix + '/download-comparison-table'
const metrics4ComparisonUrl: string = urlPrefix + '/metrics-for-comparison'
// what do these do?
const csrfToken = '{{csrf_token}}';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken})

@Injectable({
  providedIn: 'root'
})
export class ComparisonService {

  constructor(private httpClient: HttpClient) {
  }

  getValidationsIds(validations: ValidationrunDto[]): string[] {
    // get the ids of the validations
    let ids = []
    for (let validation of validations){
      ids.push(validation.id)
    }
    return ids
  }

  getMetrics4Comparison(params: any): Observable<MetricsComparisonDto[]> {
    // return all the metrics for the comparison configuration
    return this.httpClient.get<MetricsComparisonDto[]>(metrics4ComparisonUrl, {params})
  }

  getComparisonTable(params: any): Observable<any> {
    // create htm table in comparison page
    return this.httpClient.get(comparisonTableUrl, {params, headers, responseType: 'text'});
  }

  downloadComparisonTableCsv(ids: string, metric_list:string[], get_intersection:boolean, extent:string): void {
    // download comparison table
    const fileUrl = `${downloadComparisonTableUrl}?validationId=${ids}&metric_list=${metric_list}
    &get_intersecton=${get_intersection}&extent=${extent}`;
    saveAs(fileUrl);
  }

  getComparisonPlots(params: any): Observable<any> {
    return this.httpClient.get<string[]>(comparisonPlotsUrl, {params});
  }
}

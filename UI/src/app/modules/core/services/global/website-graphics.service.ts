import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';

const urlPrefix = environment.API_URL + 'api';
const getPlotUrl: string = urlPrefix + '/get-graphic-file';
@Injectable({
  providedIn: 'root'
})
export class WebsiteGraphicsService {

  constructor(private httpClient: HttpClient) { }

  getPlot(params: any): Observable<any>{
    return this.httpClient.get(getPlotUrl, {params, responseType: 'text'});
  }
}

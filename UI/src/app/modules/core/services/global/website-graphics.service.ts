import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {PlotDto} from './plot.dto';

const urlPrefix = environment.API_URL + 'api';
const getPlotsUrl: string = urlPrefix + '/get-graphic-file';
@Injectable({
  providedIn: 'root'
})
export class WebsiteGraphicsService {

  constructor(private httpClient: HttpClient) { }

  getPlots(params: any): Observable<PlotDto[]>{
    return this.httpClient.get<PlotDto[]>(getPlotsUrl, {params});
  }
}

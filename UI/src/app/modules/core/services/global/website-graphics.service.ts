import {Injectable, Optional} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {PlotDto} from './plot.dto';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';

const urlPrefix = environment.API_URL + 'api';
const getPlotsUrl: string = urlPrefix + '/get-graphic-file';
@Injectable({
  providedIn: 'root'
})
export class WebsiteGraphicsService {

  plotPrefix = 'data:image/png;base64,';
  constructor(private httpClient: HttpClient,
              private domSanitizer: DomSanitizer) { }

  getPlots(params: any): Observable<PlotDto[]>{
    return this.httpClient.get<PlotDto[]>(
      getPlotsUrl, {params});
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.domSanitizer.bypassSecurityTrustUrl(this.plotPrefix + plotBase64);
  }
  sanitizeManyPlotUrls(plotObjectList: PlotDto[]): SafeUrl[]{
    const urlList = [];
    plotObjectList.forEach(plot => {
      urlList.push(this.sanitizePlotUrl(plot.plot));
    });
    return urlList;
  }

}

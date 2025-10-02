import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import { PlotDto } from './plot.dto';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { catchError } from 'rxjs/operators';
import { HttpErrorService } from './http-error.service';

const urlPrefix = environment.API_URL + 'api';
const getPlotsUrl: string = urlPrefix + '/get-graphic-files';

@Injectable({
  providedIn: 'root'
})
export class WebsiteGraphicsService {

  plotPrefix = 'data:image/png;base64,';

  constructor(private httpClient: HttpClient,
    private domSanitizer: DomSanitizer,
    private httpError: HttpErrorService,
    private http: HttpClient) {
  }

  getPlots(params: any): Observable<PlotDto[]> {
    return this.httpClient.get<PlotDto[]>(getPlotsUrl, { params })
      .pipe(
        catchError(err => this.httpError.handleError(err,
          'Result plots are temporarily unavailable. ',
          'Files not available'))
      );
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.domSanitizer.bypassSecurityTrustUrl(this.plotPrefix + plotBase64);
  }

  getValidationMetadata(validationId: string, possibleLayers: any): Observable<any> {
    return this.httpClient.post(`${urlPrefix}/${validationId}/metadata/`, {
      possible_layers: possibleLayers
    }).pipe(
      catchError(err => this.httpError.handleError(err,
        'Validation metadata is temporarily unavailable.',
        'Metadata not available'))
    );
  }

  getLayerRange(validationId: string, metricName: string, index: number): Observable<{ vmin: number, vmax: number }> {
    return this.http.get<{ vmin: number, vmax: number }>(
      `/api/${validationId}/range/${metricName}/${index}/`
    );
  }

  getPixelValue(validationId: string, x: number, y: number): Observable<any> {
    const params = new HttpParams()
      .set('x', x.toString())
      .set('y', y.toString());

    return this.httpClient.get<any>(`${urlPrefix}/${validationId}/pixel-value/`, { params }).pipe(
      catchError(err => this.httpError.handleError(err,
        'Pixel data is temporarily unavailable.',
        'Pixel data not available'))
    );
  }
} 

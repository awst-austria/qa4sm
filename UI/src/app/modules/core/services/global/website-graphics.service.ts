import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import { PlotDto } from './plot.dto';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { catchError } from 'rxjs/operators';
import { HttpErrorService } from './http-error.service';

const urlPrefix = environment.API_URL + 'api';
const getPlotsUrl: string = urlPrefix + '/get-graphic-files';
const getTiffMapUrl: string = urlPrefix + '/get-tiff-layers';

@Injectable({
  providedIn: 'root'
})
export class WebsiteGraphicsService {

  plotPrefix = 'data:image/png;base64,';

  constructor(private httpClient: HttpClient,
              private domSanitizer: DomSanitizer,
              private httpError: HttpErrorService) {
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


  getAvailableTiffLayers(validationId: string): Observable<any> {
    const updatedUrl = getTiffMapUrl + '/' + validationId + '/';
    return this.httpClient.get<any>(updatedUrl).pipe(
      catchError(err => this.httpError.handleError(err,
        'Tiff file is not available for this validation. Plotted maps provided instead.',
        'File not available'))
    );
  }

}

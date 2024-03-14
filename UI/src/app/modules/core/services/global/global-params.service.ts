import {Injectable} from '@angular/core';
import {environment} from '../../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {GlobalParamsDto} from './global-params.dto';
import {catchError} from 'rxjs/operators';
import {HttpErrorService} from './http-error.service';

const globalContextUrl: string = environment.API_URL + 'api/globals';

@Injectable({
  providedIn: 'root'
})
export class GlobalParamsService {

  // we can actually provide some hard coded information in case there is an error with the http response
  public globalContext: GlobalParamsDto = {
    admin_mail: 'support (at) qa4sm.eu',
    doi_prefix: '',
    site_url: 'qa4sm.eu/ui',
    app_version: '2.*.*',
    expiry_period: '60',
    warning_period: '7',
    temporal_matching_default: 12
  };

  tooltipLifetime = 2000; // needed to set it somewhere global;

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
    this.init();
  }

  private init(): void {
    this.httpClient
      .get<GlobalParamsDto>(globalContextUrl)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      )
      .subscribe(
        data => {
          this.globalContext = data;
        }
      );
  }

}

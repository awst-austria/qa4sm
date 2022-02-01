import { Injectable } from '@angular/core';
import {environment} from '../../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {GlobalParamsDto} from './global-params.dto';

const globalContextUrl: string = environment.API_URL + 'api/globals';

@Injectable({
  providedIn: 'root'
})
export class GlobalParamsService {

  // globalContext$: Observable<GlobalContextDto[]>;
  public globalContext: GlobalParamsDto = {
  admin_mail: '',
  doi_prefix: '',
  site_url: '',
  app_version: '',
  expiry_period: '',
  warning_period: '',
  };

  constructor(private httpClient: HttpClient) {
    this.init();
  }

  private init() {
    this.httpClient
      .get<GlobalParamsDto>(globalContextUrl)
      .subscribe(
        data => {
          this.globalContext = data;
        },
        error => {

        }
      );
  }

}

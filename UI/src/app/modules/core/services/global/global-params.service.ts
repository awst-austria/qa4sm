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

  // globalContext$: Observable<GlobalContextDto[]>;
  public globalContext: GlobalParamsDto;
  tooltipLifetime = 2000; // needed to set it somewhere global;

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
    this.init();
  }

  private init(): void{
    this.httpClient
      .get<GlobalParamsDto>(globalContextUrl)
      .pipe(
        catchError(err => this.httpError.handleError(err)) //todo: here I can actually mock data in case of server error
      )
      .subscribe(
        data => {
          this.globalContext = data;
        }
      );
  }

}

import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {Observable} from 'rxjs';
import {CountryDto} from '../global/country.dto';
import {catchError} from 'rxjs/operators';
import {HttpErrorService} from '../global/http-error.service';

const countriesUrl: string = environment.API_URL + 'api/country-list';

@Injectable({
  providedIn: 'root'
})
export class LocalApiService {

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) { }

  getCountryList(): Observable<CountryDto[]>{
    return this.httpClient.get<CountryDto[]>(countriesUrl)
      .pipe(catchError(error => this.httpError.handleError(error)));
  }

}

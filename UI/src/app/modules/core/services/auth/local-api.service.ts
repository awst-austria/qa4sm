import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {Observable} from 'rxjs';
import {CountryDto} from '../global/country.dto';

const countriesUrl: string = environment.API_URL + 'api/country-list';

@Injectable({
  providedIn: 'root'
})
export class LocalApiService {

  constructor(private httpClient: HttpClient) { }

  getCountryList(): Observable<CountryDto[]>{
    return this.httpClient.get<CountryDto[]>(countriesUrl);
  }

}

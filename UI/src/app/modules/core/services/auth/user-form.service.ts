import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {Observable} from 'rxjs';

const countriesUrl: string = environment.API_URL + 'api/country-list';

@Injectable({
  providedIn: 'root'
})
export class UserFormService {

  constructor(private httpClient: HttpClient) { }

  getCountryList(): Observable<any>{
    return this.httpClient.get(countriesUrl);
  }
}

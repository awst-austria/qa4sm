import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environment';
import {ValidationSetDto} from './validation.set.dto';

const publishedValidationRunUrl: string = environment.API_URL + 'api/published-results';
const customValidationRunUrl: string = environment.API_URL + 'api/my-results';

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {

  customValidationrun$: Observable<ValidationSetDto>;
  publishedValidationrun$: Observable<ValidationSetDto>;

  constructor(private httpClient: HttpClient) {
  }

  getMyValidationruns(params: any): Observable<ValidationSetDto>{
    this.customValidationrun$ = this.httpClient.get<ValidationSetDto>(customValidationRunUrl, {params});
    return  this.customValidationrun$;
  }

  getPublishedValidationruns(params: any): Observable<ValidationSetDto>{
    this.publishedValidationrun$ = this.httpClient.get<ValidationSetDto>(publishedValidationRunUrl, {params});
    return  this.publishedValidationrun$;
  }
}

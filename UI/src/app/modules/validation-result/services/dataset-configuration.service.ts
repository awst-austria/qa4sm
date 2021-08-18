import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {DatasetConfigurationDto} from './dataset-configuration.dto';
import {shareReplay} from 'rxjs/operators';

const CONFIGURATION_URL: string = environment.API_URL + 'api/dataset-configuration';
const CACHE_VAL_ID = '00000000-0000-0000-0000-000000000000';
const CACHE_CONFIG_ID = -1;

export class ConfigurationCacheItem {
  constructor(public lastFetched: Date, public configuration$: Observable<DatasetConfigurationDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class DatasetConfigurationService {

  requestCacheString = new Map<string, ConfigurationCacheItem>();
  requestCacheNumber = new Map<number, ConfigurationCacheItem>();

  constructor(private httpClient: HttpClient) {
    this.requestCacheString.set(
      CACHE_VAL_ID,
      new ConfigurationCacheItem(new Date(), this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL).pipe(shareReplay())));
    this.requestCacheNumber.set(
      CACHE_CONFIG_ID,
      new ConfigurationCacheItem(new Date(), this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL).pipe(shareReplay())));
  }
  getAllConfigs(): Observable<DatasetConfigurationDto[]> {
    return this.getConfigByValidationrun(CACHE_VAL_ID);
  }

  getConfigByValidationrun(validationrunId: string): Observable<DatasetConfigurationDto[]> {
    let request;
    if (validationrunId === CACHE_VAL_ID) {
      request = this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('validationrun', String(validationrunId));
      request = this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL, {params: params}).pipe(shareReplay());
    }

    let cacheItem = new ConfigurationCacheItem(new Date(), request);
    this.requestCacheString.set(validationrunId, cacheItem);

    return request;
  }
}

import { Injectable } from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {DatasetConfigurationDto} from './dataset-configuration.dto';
import {shareReplay} from 'rxjs/operators';

const CONFIGURATION_URL: string = environment.API_URL + 'api/configuration';
const CACHE_LIFETIME: number = 5 * 60 * 1000; // 5 minutes
const CACHE_KEY_ALL_VERSIONS = -1;

export class ConfigurationCacheItem {
  constructor(public lastFetched: Date, public configuration$: Observable<DatasetConfigurationDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class DatasetConfigurationService {

  requestCache = new Map<number, ConfigurationCacheItem>();

  constructor(private httpClient: HttpClient) {
    this.requestCache.set(
      CACHE_KEY_ALL_VERSIONS,
      new ConfigurationCacheItem(new Date(), this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL).pipe(shareReplay())));
  }
  getAllConfigs(): Observable<DatasetConfigurationDto[]> {
    return this.getConfigByValidationrun(CACHE_KEY_ALL_VERSIONS);
  }

  getConfigByValidationrun(validationrunId: number): Observable<DatasetConfigurationDto[]> {
    let request;
    if (validationrunId === CACHE_KEY_ALL_VERSIONS) {
      request = this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('validationrun', String(validationrunId));
      request = this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL, {params: params}).pipe(shareReplay());
    }

    let cacheItem = new ConfigurationCacheItem(new Date(), request);
    this.requestCache.set(validationrunId, cacheItem);

    return request;
  }
}

import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {DatasetConfigurationDto} from './dataset-configuration.dto';
import {shareReplay} from 'rxjs/operators';
import {DataCache} from '../../core/tools/DataCache';

const CONFIGURATION_URL: string = environment.API_URL + 'api/dataset-configuration';
const CONFIGURATION_BY_DATASET_URL: string = environment.API_URL + 'api/dataset-configuration-by-dataset';
const CACHE_KEY_ALL_CONFIGS = -1;

export class ConfigurationCacheItem {
  constructor(public lastFetched: Date, public configuration$: Observable<DatasetConfigurationDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class DatasetConfigurationService {

  // cache for dataset arrays
  arrayConfigRequestCache = new DataCache<Observable<DatasetConfigurationDto[]>>(5);

  constructor(private httpClient: HttpClient) {
  }
  getAllConfigs(): Observable<DatasetConfigurationDto[]> {
    if (this.arrayConfigRequestCache.isCached(CACHE_KEY_ALL_CONFIGS)){
      return this.arrayConfigRequestCache.get(CACHE_KEY_ALL_CONFIGS);
    } else {
      const configs$ = this.httpClient.get<DatasetConfigurationDto[]>(CONFIGURATION_URL).pipe(shareReplay());
      this.arrayConfigRequestCache.push(CACHE_KEY_ALL_CONFIGS, configs$);
      return configs$;
    }
  }

  getConfigByValidationrun(validationrunId: string): Observable<DatasetConfigurationDto[]> {
    const getUrl = CONFIGURATION_BY_DATASET_URL + '/' + validationrunId;
    return this.httpClient.get<DatasetConfigurationDto[]>(getUrl);

  }
}

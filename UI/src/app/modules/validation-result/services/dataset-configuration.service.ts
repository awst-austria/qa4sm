import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {DatasetConfigurationDto} from './dataset-configuration.dto';
import {DataCache} from '../../core/tools/DataCache';

const CONFIGURATION_URL: string = environment.API_URL + 'api/dataset-configuration';
const CACHE_KEY_ALL_CONFIGS = -1;


@Injectable({
  providedIn: 'root'
})
export class DatasetConfigurationService {

  // cache for dataset arrays
  arrayConfigRequestCache = new DataCache<Observable<DatasetConfigurationDto[]>>(5);

  constructor(private httpClient: HttpClient) {
  }

  getConfigByValidationrun(validationrunId: string): Observable<DatasetConfigurationDto[]> {
    const getUrl = CONFIGURATION_URL + '/' + validationrunId;
    return this.httpClient.get<DatasetConfigurationDto[]>(getUrl);

  }
}

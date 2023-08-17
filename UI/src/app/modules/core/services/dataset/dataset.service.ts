import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {DatasetDto} from './dataset.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';

const datasetUrl: string = environment.API_URL + 'api/dataset';
const CACHE_KEY_ALL_DATASETS = -1;
const CACHE_USER_DATA_INFO = -2;
const CACHE_FILE_INFO = -2;

@Injectable({
  providedIn: 'root'
})
export class DatasetService {

  // cache for dataset arrays
  arrayRequestCache = new DataCache<Observable<DatasetDto[]>>(5);
  // cache for single dataset dtos
  singleRequestCache = new DataCache<Observable<DatasetDto>>(5);
  // cache for information if user data should be also fetched
  userDataInfoCache = new DataCache<boolean>(5);
  userFileInfoCache = new DataCache<boolean>(5);

  constructor(private httpClient: HttpClient) {
  }

  getAllDatasets(userData = false, excludeNoFiles = true): Observable<DatasetDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_DATASETS) && this.userDataInfoCache
      .get(CACHE_USER_DATA_INFO) === userData && this.userDataInfoCache.get(CACHE_FILE_INFO) === excludeNoFiles) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_DATASETS);
    } else {
      const params = new HttpParams().set('userData', String(userData))
        .set('excludeNoFiles', String(excludeNoFiles));
      const datasets$ = this.httpClient.get<DatasetDto[]>(datasetUrl, {params})
        .pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_DATASETS, datasets$);
      this.userDataInfoCache.push(CACHE_USER_DATA_INFO, userData);
      this.userDataInfoCache.push(CACHE_FILE_INFO, excludeNoFiles);
      return datasets$;
    }
  }

  getDatasetById(datasetId: number): Observable<DatasetDto> {
    if (this.singleRequestCache.isCached(datasetId)) {
      return this.singleRequestCache.get(datasetId);
    } else {
      let getURL = datasetUrl + '/' + datasetId;
      let dataset$ = this.httpClient.get<DatasetDto>(getURL).pipe(shareReplay());
      this.singleRequestCache.push(datasetId, dataset$);
      return dataset$;
    }
  }

}

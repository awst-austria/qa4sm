import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {DatasetVariableDto} from './dataset-variable.dto';

const DATASET_VARIABLE_URL: string = environment.API_URL + 'api/dataset-variable';
const CACHE_LIFETIME: number = 5 * 60 * 1000; // 5 minutes
const CACHE_KEY_ALL_VERSIONS = -1;

export class DatasetVariableCacheItem {
  constructor(public lastFetched: Date, public datasetVariables$: Observable<DatasetVariableDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class DatasetVariableService {

  requestCache = new Map<number, DatasetVariableCacheItem>();


  constructor(private httpClient: HttpClient) {
    this.requestCache.set(
      CACHE_KEY_ALL_VERSIONS,
      new DatasetVariableCacheItem(new Date(), this.httpClient.get<DatasetVariableDto[]>(DATASET_VARIABLE_URL).pipe(shareReplay())));
  }

  getAllVersions(): Observable<DatasetVariableDto[]> {
    return this.getVariablesByDataset(CACHE_KEY_ALL_VERSIONS);
  }

  getVariablesByDataset(datasetId: number): Observable<DatasetVariableDto[]> {
    if (this.isCached(datasetId)) {
      return this.requestCache.get(datasetId).datasetVariables$;
    }

    let request;
    if (datasetId == CACHE_KEY_ALL_VERSIONS) {
      request = this.httpClient.get<DatasetVariableDto[]>(DATASET_VARIABLE_URL).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('dataset', String(datasetId));
      request = this.httpClient.get<DatasetVariableDto[]>(DATASET_VARIABLE_URL, {params: params}).pipe(shareReplay());
    }

    let cacheItem = new DatasetVariableCacheItem(new Date(), request);
    this.requestCache.set(datasetId, cacheItem);

    return request;
  }

  /**
   * Checks whether there is valid cache item for the specified datasetId
   * @param datasetId
   * @private
   */
  private isCached(datasetId: number): boolean {
    if (this.requestCache.has(datasetId)) {
      let cacheItem = this.requestCache.get(datasetId);
      if (((new Date()).getTime() - cacheItem.lastFetched.getTime()) < CACHE_LIFETIME) {
        return true;
      }
    }

    return false;
  }
}

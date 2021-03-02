import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environment';
import {DatasetVersionDto} from './dataset-version.dto';
import {HttpClient, HttpParams} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';

const datasetVersionUrl: string = environment.API_URL + 'api/dataset-version';
const CACHE_LIFETIME: number = 5 * 60 * 1000; // 5 minutes
const CACHE_KEY_ALL_VERSIONS = -1;
const CACHE_KEY_VERSION = -1;

export class DatasetVersionCacheItem {
  constructor(public lastFetched: Date, public datasetVersions$: Observable<DatasetVersionDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class DatasetVersionService {

  requestCacheAll = new Map<number, DatasetVersionCacheItem>();
  requestCacheOne = new Map<number, DatasetVersionCacheItem>();


  constructor(private httpClient: HttpClient) {
    this.requestCacheAll.set(
      CACHE_KEY_ALL_VERSIONS,
      new DatasetVersionCacheItem(new Date(), this.httpClient.get<DatasetVersionDto[]>(datasetVersionUrl).pipe(shareReplay())));
    this.requestCacheOne.set(
      CACHE_KEY_VERSION,
      new DatasetVersionCacheItem(new Date(), this.httpClient.get<DatasetVersionDto[]>(datasetVersionUrl).pipe(shareReplay())));
  }

  getAllVersions(): Observable<DatasetVersionDto[]> {
    return this.getVersionsByDataset(CACHE_KEY_ALL_VERSIONS);
  }

  getVersionsByDataset(datasetId: number): Observable<DatasetVersionDto[]> {
    if (this.isCached(datasetId)) {
      return this.requestCacheAll.get(datasetId).datasetVersions$;
    }

    let request;
    if (datasetId == CACHE_KEY_ALL_VERSIONS) {
      request = this.httpClient.get<DatasetVersionDto[]>(datasetVersionUrl).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('dataset', String(datasetId));
      request = this.httpClient.get<DatasetVersionDto[]>(datasetVersionUrl, {params: params}).pipe(shareReplay());
    }

    let cacheItem = new DatasetVersionCacheItem(new Date(), request);
    this.requestCacheAll.set(datasetId, cacheItem);

    return request;
  }

  getVersionById(versionId: number): Observable<DatasetVersionDto>{
    let request;
    if (versionId === CACHE_KEY_VERSION) {
      request = this.httpClient.get<DatasetVersionDto>(datasetVersionUrl).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('version_id', String(versionId));
      request = this.httpClient.get<DatasetVersionDto>(datasetVersionUrl, {params: params}).pipe(shareReplay());
    }

    let cacheItem = new DatasetVersionCacheItem(new Date(), request);
    this.requestCacheOne.set(versionId, cacheItem);

    return request;

  }

  /**
   * Checks whether there is valid cache item for the specified datasetId
   * @param datasetId
   * @private
   */
  private isCached(datasetId: number): boolean {
    if (this.requestCacheAll.has(datasetId)) {
      let cacheItem = this.requestCacheAll.get(datasetId);
      if (((new Date()).getTime() - cacheItem.lastFetched.getTime()) < CACHE_LIFETIME) {
        return true;
      }
    }

    return false;
  }
}

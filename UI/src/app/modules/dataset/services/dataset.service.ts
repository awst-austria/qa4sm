import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {DatasetDto} from './dataset.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environment';
import {shareReplay} from 'rxjs/operators';

const datasetUrl: string = environment.API_URL + 'api/dataset';
const CACHE_LIFETIME: number = 5 * 60 * 1000; // 5 minutes
const CACHE_KEY_ALL_DATASETS = -1;

export class DatasetCacheItem {
  constructor(public lastFetched: Date, public configuration$: Observable<DatasetDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class DatasetService {

  datasets$: Observable<DatasetDto[]>;
  datasetsCreatedOn: Date;
  requestCache = new Map<number, DatasetCacheItem>();

  constructor(private httpClient: HttpClient) {
    this.datasets$ = this.httpClient.get<DatasetDto[]>(datasetUrl).pipe(shareReplay());
    this.datasetsCreatedOn = new Date();
    this.requestCache.set(
      CACHE_KEY_ALL_DATASETS,
      new DatasetCacheItem(new Date(), this.httpClient.get<DatasetDto[]>(datasetUrl).pipe(shareReplay())));
  }

  getAllDatasets(): Observable<DatasetDto[]> {
    if (((new Date()).getTime() - this.datasetsCreatedOn.getTime()) > CACHE_LIFETIME) {
      this.datasets$ = this.httpClient.get<DatasetDto[]>(datasetUrl).pipe(shareReplay());
      this.datasetsCreatedOn = new Date();
    }
    return this.datasets$;
  }

  getDatasetById(datasetId: number): Observable<DatasetDto> {
    let request;
    if (datasetId === CACHE_KEY_ALL_DATASETS) {
      request = this.httpClient.get<DatasetDto>(datasetUrl).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('dataset_id', String(datasetId));
      request = this.httpClient.get<DatasetDto>(datasetUrl, {params: params}).pipe(shareReplay());
    }
    let cacheItem = new DatasetCacheItem(new Date(), request);
    this.requestCache.set(datasetId, cacheItem);

    return request;
  }

}

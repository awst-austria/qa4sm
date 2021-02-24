import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';
import {environment} from '../../../../environments/environment';
import {FilterDto} from './filter.dto';


const dataFilterUrl: string = environment.API_URL + 'api/data-filter';
const CACHE_LIFETIME: number = 5 * 60 * 1000; // 5 minutes
const CACHE_KEY_ALL_FILTERS = -1;

export class DataFilterCacheItem {
  constructor(public lastFetched: Date, public dataFilters$: Observable<FilterDto[]>) {
  }
}

@Injectable({
  providedIn: 'root'
})
export class FilterService {

  requestCache = new Map<number, DataFilterCacheItem>();


  constructor(private httpClient: HttpClient) {
    this.requestCache.set(
      CACHE_KEY_ALL_FILTERS,
      new DataFilterCacheItem(new Date(), this.httpClient.get<FilterDto[]>(dataFilterUrl).pipe(shareReplay())));
  }

  getAllFilters(): Observable<FilterDto[]> {
    return this.getFilterByDatasetId(CACHE_KEY_ALL_FILTERS);
  }

  getFilterByDatasetId(datasetId: number): Observable<FilterDto[]> {
    if (this.isCached(datasetId)) {
      return this.requestCache.get(datasetId).dataFilters$;
    }

    let request;
    if (datasetId == CACHE_KEY_ALL_FILTERS) {
      request = this.httpClient.get<FilterDto[]>(dataFilterUrl).pipe(shareReplay());
    } else {
      let params = new HttpParams().set('dataset', String(datasetId));
      request = this.httpClient.get<FilterDto[]>(dataFilterUrl, {params: params}).pipe(shareReplay());
    }

    let cacheItem = new DataFilterCacheItem(new Date(), request);
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


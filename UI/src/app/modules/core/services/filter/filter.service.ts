import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';
import {environment} from '../../../../../environments/environment';
import {FilterDto} from './filter.dto';
import {DataCache} from '../../tools/DataCache';
import {ParameterisedFilterDto} from './parameterised-filter.dto';


const dataFilterUrl: string = environment.API_URL + 'api/data-filter';
const dataParameterisedFilterUrl: string = environment.API_URL + 'api/param-filter';
const CACHE_KEY_ALL_FILTERS = -1;


@Injectable({
  providedIn: 'root'
})
export class FilterService {

  //cache for filter arrays
  arrayRequestCache = new DataCache<Observable<FilterDto[]>>(5);
  arrayRequestCacheParam = new DataCache<Observable<ParameterisedFilterDto[]>>(5);
  //cache for single filter dtos
  singleRequestCache = new DataCache<Observable<FilterDto>>(5);
  singleRequestCacheParam = new DataCache<Observable<ParameterisedFilterDto>>(5);


  constructor(private httpClient: HttpClient) {
  }

  getAllFilters(): Observable<FilterDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_FILTERS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_FILTERS);
    } else {
      let filters$ = this.httpClient.get<FilterDto[]>(dataFilterUrl).pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_FILTERS, filters$);
      return filters$;
    }
  }

  getFiltersByDatasetId(datasetId: number): Observable<FilterDto[]> {
    if (this.arrayRequestCache.isCached(datasetId)) {
      return this.arrayRequestCache.get(datasetId);
    } else {
      let params = new HttpParams().set('dataset', String(datasetId));
      let filters$ = this.httpClient.get<FilterDto[]>(dataFilterUrl, {params: params}).pipe(shareReplay());
      this.arrayRequestCache.push(datasetId, filters$);
      return filters$;
    }
  }

  // getFilterById(filterId: number): Observable<FilterDto> {
  //   if (this.singleRequestCache.isCached(filterId)) {
  //     return this.singleRequestCache.get(filterId);
  //   } else {
  //     const getURL = dataFilterUrl + '/' + filterId;
  //     const filter$ = this.httpClient.get<FilterDto>(getURL).pipe(shareReplay());
  //     this.singleRequestCache.push(filterId, filter$);
  //     return filter$;
  //   }
  // }

  getAllParameterisedFilters(): Observable<ParameterisedFilterDto[]> {
    if (this.arrayRequestCacheParam.isCached(CACHE_KEY_ALL_FILTERS)) {
      return this.arrayRequestCacheParam.get(CACHE_KEY_ALL_FILTERS);
    } else {
      const paramFilters$ = this.httpClient.get<ParameterisedFilterDto[]>(dataParameterisedFilterUrl).pipe(shareReplay());
      this.arrayRequestCacheParam.push(CACHE_KEY_ALL_FILTERS, paramFilters$);
      return paramFilters$;
    }
  }

  // getParameterisedFilterByConfig(configId: number): Observable<ParameterisedFilterDto[]> {
  //   if (this.arrayRequestCacheParam.isCached(configId)) {
  //     return this.arrayRequestCacheParam.get(configId);
  //   } else {
  //     const params = new HttpParams().set('config', String(configId));
  //     const paramFilters$ = this.httpClient.get<ParameterisedFilterDto[]>(dataParameterisedFilterUrl, {params}).pipe(shareReplay());
  //     this.arrayRequestCacheParam.push(configId, paramFilters$);
  //     return paramFilters$;
  //   }
  // }

  // getParameterisedFilterById(paramFilterId: number): Observable<ParameterisedFilterDto> {
  //   if (this.singleRequestCacheParam.isCached(paramFilterId)) {
  //     return this.singleRequestCacheParam.get(paramFilterId);
  //   } else {
  //     const getURL = dataParameterisedFilterUrl + '/' + paramFilterId;
  //     const paramFilter$ = this.httpClient.get<ParameterisedFilterDto>(getURL).pipe(shareReplay());
  //     this.singleRequestCacheParam.push(paramFilterId, paramFilter$);
  //     return paramFilter$;
  //   }
  // }

}


import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {catchError, shareReplay} from 'rxjs/operators';
import {environment} from '../../../../../environments/environment';
import {FilterDto} from './filter.dto';
import {DataCache} from '../../tools/DataCache';
import {ParameterisedFilterDto} from './parameterised-filter.dto';
import {HttpErrorService} from '../global/http-error.service';


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


  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
  }

  getAllFilters(): Observable<FilterDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_FILTERS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_FILTERS);
    } else {
      let filters$ = this.httpClient.get<FilterDto[]>(dataFilterUrl).pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_FILTERS, filters$);
      return filters$
        .pipe(
          catchError(err => this.httpError.handleError(err))
        );
    }
  }

  getFiltersByVersionId(datasetId: number): Observable<FilterDto[]> {
    if (this.arrayRequestCache.isCached(datasetId)) {
      return this.arrayRequestCache.get(datasetId);
    } else {
      // let params = new HttpParams().set('dataset', String(datasetId));
      let getUrl = dataFilterUrl + '/' + datasetId;
      let filters$ = this.httpClient.get<FilterDto[]>(getUrl).pipe(shareReplay());
      this.arrayRequestCache.push(datasetId, filters$);
      return filters$
        .pipe(
          catchError(err => this.httpError.handleError(err))
        );
    }
  }

  getAllParameterisedFilters(): Observable<ParameterisedFilterDto[]> {
    if (this.arrayRequestCacheParam.isCached(CACHE_KEY_ALL_FILTERS)) {
      return this.arrayRequestCacheParam.get(CACHE_KEY_ALL_FILTERS);
    } else {
      const paramFilters$ = this.httpClient.get<ParameterisedFilterDto[]>(dataParameterisedFilterUrl).pipe(shareReplay());
      this.arrayRequestCacheParam.push(CACHE_KEY_ALL_FILTERS, paramFilters$);
      return paramFilters$
        .pipe(
          catchError(err => this.httpError.handleError(err))
        );
    }
  }


}


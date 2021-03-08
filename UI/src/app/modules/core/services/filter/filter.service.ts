import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';
import {environment} from '../../../../../environments/environment';
import {FilterDto} from './filter.dto';
import {DataCache} from '../../tools/DataCache';


const dataFilterUrl: string = environment.API_URL + 'api/data-filter';
const CACHE_KEY_ALL_FILTERS = -1;


@Injectable({
  providedIn: 'root'
})
export class FilterService {

  //cache for dataset arrays
  arrayRequestCache = new DataCache<Observable<FilterDto[]>>(5);


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
}


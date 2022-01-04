import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {DatasetVersionDto} from './dataset-version.dto';
import {HttpClient, HttpParams} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';

const DATASET_VERSION_URL: string = environment.API_URL + 'api/dataset-version';
const CACHE_KEY_ALL_VERSIONS = -1;

@Injectable({
  providedIn: 'root'
})
export class DatasetVersionService {

  //cache for dataset version arrays
  arrayRequestCache = new DataCache<Observable<DatasetVersionDto[]>>(5);
  //cache for single dataset version dtos
  singleRequestCache = new DataCache<Observable<DatasetVersionDto>>(5);


  constructor(private httpClient: HttpClient) {
  }

  getAllVersions(): Observable<DatasetVersionDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_VERSIONS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_VERSIONS);
    } else {
      let datasetVersions$ = this.httpClient.get<DatasetVersionDto[]>(DATASET_VERSION_URL).pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_VERSIONS, datasetVersions$);
      return datasetVersions$;
    }
  }

  getVersionsByDataset(datasetId: number): Observable<DatasetVersionDto[]> {
    if (this.arrayRequestCache.isCached(datasetId)) {
      return this.arrayRequestCache.get(datasetId);
    } else {
      let params = new HttpParams().set('dataset', String(datasetId));
      let datasetVariables$ = this.httpClient.get<DatasetVersionDto[]>(DATASET_VERSION_URL, {params: params}).pipe(shareReplay());
      this.arrayRequestCache.push(datasetId, datasetVariables$);
      return datasetVariables$;
    }
  }

  getVersionById(versionId: number): Observable<DatasetVersionDto> {
    if (this.singleRequestCache.isCached(versionId)) {
      return this.singleRequestCache.get(versionId);
    } else {
      let getURL = DATASET_VERSION_URL + '/' + versionId;
      let datasetVersion$ = this.httpClient.get<DatasetVersionDto>(getURL).pipe(shareReplay());
      this.singleRequestCache.push(versionId, datasetVersion$);
      return datasetVersion$;
    }

  }

}

import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {DatasetVersionDto} from './dataset-version.dto';
import {HttpClient} from '@angular/common/http';
import {shareReplay} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';

const DATASET_VERSION_URL: string = environment.API_URL + 'api/dataset-version';
const DATASET_VERSION_GEOJSON_URL: string = environment.API_URL + 'api/dataset-version-geojson';
const CACHE_KEY_ALL_VERSIONS = -1;

@Injectable({
  providedIn: 'root'
})
export class DatasetVersionService {

  // cache for dataset version arrays
  arrayRequestCache = new DataCache<Observable<DatasetVersionDto[]>>(5);
  // cache for single dataset version dtos
  singleRequestCache = new DataCache<Observable<DatasetVersionDto>>(5);


  constructor(private httpClient: HttpClient) {
  }

  getAllVersions(): Observable<DatasetVersionDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_VERSIONS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_VERSIONS);
    } else {
      const datasetVersions$ = this.httpClient.get<DatasetVersionDto[]>(DATASET_VERSION_URL).pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_VERSIONS, datasetVersions$);
      return datasetVersions$;
    }
  }

  getVersionsByDataset(datasetId: number): Observable<DatasetVersionDto[]> {
    if (this.arrayRequestCache.isCached(datasetId)) {
      return this.arrayRequestCache.get(datasetId);
    } else {
      const getUrl = DATASET_VERSION_URL + '-by-dataset/' + datasetId;
      const datasetVariables$ = this.httpClient.get<DatasetVersionDto[]>(getUrl).pipe(shareReplay());
      this.arrayRequestCache.push(datasetId, datasetVariables$);
      return datasetVariables$;
    }
  }

  getVersionById(versionId: number): Observable<DatasetVersionDto> {
    if (this.singleRequestCache.isCached(versionId)) {
      return this.singleRequestCache.get(versionId);
    } else {
      const getURL = DATASET_VERSION_URL + '/' + versionId;
      const datasetVersion$ = this.httpClient.get<DatasetVersionDto>(getURL).pipe(shareReplay());
      this.singleRequestCache.push(versionId, datasetVersion$);
      return datasetVersion$;
    }
  }

  getGeoJSONById(versionId:number):Observable<any>{
    const getURL = DATASET_VERSION_GEOJSON_URL + '/' + versionId;
    return this.httpClient.get<any>(getURL).pipe(shareReplay());
  }

}

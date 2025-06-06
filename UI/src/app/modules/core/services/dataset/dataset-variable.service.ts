import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, shareReplay } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { environment } from '../../../../../environments/environment';
import { DatasetVariableDto } from './dataset-variable.dto';
import { DataCache } from '../../tools/DataCache';
import { HttpErrorService } from '../global/http-error.service';

const DATASET_VARIABLE_URL: string = environment.API_URL + 'api/dataset-variable';
const CACHE_KEY_ALL_VERSIONS = -1;


@Injectable({
  providedIn: 'root'
})
export class DatasetVariableService {

  // cache for dataset arrays
  arrayRequestCache = new DataCache<Observable<DatasetVariableDto[]>>(5);
  // cache for single dataset dtos
  singleRequestCache = new DataCache<Observable<DatasetVariableDto>>(5);


  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
  }

  getAllVariables(): Observable<DatasetVariableDto[]> {
    if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_VERSIONS)) {
      return this.arrayRequestCache.get(CACHE_KEY_ALL_VERSIONS);
    } else {
      let datasetVariables$ = this.httpClient.get<DatasetVariableDto[]>(DATASET_VARIABLE_URL).pipe(shareReplay());
      this.arrayRequestCache.push(CACHE_KEY_ALL_VERSIONS, datasetVariables$);
      return datasetVariables$
        .pipe(
          catchError(err => this.httpError.handleError(err, 'We could not fetch variables.'))
        );
    }

  }

  getVariablesByVersion(versionId: number): Observable<DatasetVariableDto[]> {
    if (this.arrayRequestCache.isCached(versionId)) {
      return this.arrayRequestCache.get(versionId);
    } else {
      const getUrl = DATASET_VARIABLE_URL + '-by-version/' + versionId;
      let datasetVariables$ = this.httpClient.get<DatasetVariableDto[]>(getUrl).pipe(shareReplay());
      this.arrayRequestCache.push(versionId, datasetVariables$);
      return datasetVariables$
        .pipe(
          catchError(err => this.httpError.handleError(err, 'We could not fetch variables for selected dataset.')),
        );
    }
  }

  getVariableById(variableId: number, refresh = false): Observable<DatasetVariableDto> {
    //simplified implementation for demo purposes
    if (this.singleRequestCache.isCached(variableId) && !refresh) {
      return this.singleRequestCache.get(variableId);
    } else {
      let getURL = DATASET_VARIABLE_URL + '/' + variableId;
      let datasetVariable$ = this.httpClient.get<DatasetVariableDto>(getURL).pipe(shareReplay());
      this.singleRequestCache.push(variableId, datasetVariable$);
      return datasetVariable$
        .pipe(
          catchError(err => this.httpError.handleError(err, 'We could not fetch proper variable.')),
        );
    }

  }
}

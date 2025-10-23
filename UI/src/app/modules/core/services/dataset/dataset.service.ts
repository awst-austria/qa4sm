import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {DatasetDto} from './dataset.dto';
import {Observable, of} from 'rxjs';
import {environment} from '../../../../../environments/environment';
import {catchError, map, shareReplay, switchMap, tap} from 'rxjs/operators';
import {DataCache} from '../../tools/DataCache';
import {HttpErrorService} from '../global/http-error.service';
import { UserDatasetsService } from 'src/app/modules/user-datasets/services/user-datasets.service';

// const datasetUrl: string = environment.API_URL + 'api/wrongAdress';
const datasetUrl: string = environment.API_URL + 'api/dataset';
const CACHE_KEY_ALL_DATASETS = 'allDatasets';
const CACHE_USER_DATA_INFO = 'userDataInfo';
const CACHE_FILE_INFO = 'isThereFileInfo';

// The service is responsible for loading lists of datasets 
// and a single dataset by ID from the backend, caching the results,
@Injectable({
  providedIn: 'root'
})
export class DatasetService {

  // cache for dataset arrays
  arrayRequestCache = new DataCache<Observable<DatasetDto[]>>(5);
  // cache for single dataset dtos
  singleRequestCache = new DataCache<Observable<DatasetDto>>(5);
  // cache for information if user data should be also fetched
  userDataInfoCache = new DataCache<boolean>(5);
  userFileInfoCache = new DataCache<boolean>(5);

  constructor(private httpClient: HttpClient,
    private httpError: HttpErrorService,
    private userDatasets: UserDatasetsService) {
  }

  getAllDatasets(userData = false, excludeNoFiles = true): Observable<DatasetDto[]> {

  if (this.arrayRequestCache.isCached(CACHE_KEY_ALL_DATASETS) &&
      this.userDataInfoCache.get(CACHE_USER_DATA_INFO) === userData &&
      this.userFileInfoCache.get(CACHE_FILE_INFO) === excludeNoFiles) {

    return this.arrayRequestCache.get(CACHE_KEY_ALL_DATASETS).pipe(
      catchError(err => this.httpError.handleError(err))
    );
  } else {

    const params = new HttpParams()
      .set('userData', String(userData))
      .set('excludeNoFiles', String(excludeNoFiles));

    // base stream from backend
    let datasets$ = this.httpClient.get<DatasetDto[]>(datasetUrl, { params });
    // MINIMAL addition: filter out failed user uploads if userData=true
    if (userData) {
      datasets$ = datasets$.pipe(
        switchMap((datasets: DatasetDto[]) =>
          this.userDatasets.getUserDataList().pipe(
            
            // if not logged in (401/403) or any error
            catchError(() => of([])),
            map(files => {
              const statusByDatasetId = new Map<number, string>();
              for (const f of files) {
                statusByDatasetId.set(f.dataset, (f.status ?? '').toLowerCase());
              }

              return datasets.filter(ds => {
                const isUserProvided = ds?.source_reference === 'Data provided by a user';
                if (!isUserProvided) return true; // keep non-user datasets

                const status = statusByDatasetId.get(ds.id);
                // keep only user datasets whose status is 'failed'
                return status !== 'failed';
              });
            })
          )
        )
      );
    }

    // cache the (possibly filtered) stream
    const shared$ = datasets$.pipe(shareReplay());

    this.arrayRequestCache.push(CACHE_KEY_ALL_DATASETS, shared$);
    this.userDataInfoCache.push(CACHE_USER_DATA_INFO, userData);
    this.userFileInfoCache.push(CACHE_FILE_INFO, excludeNoFiles);

    return shared$.pipe(
      catchError(err => this.httpError.handleError(err))
    );
  }
}

  getDatasetById(datasetId: number): Observable<DatasetDto> {
    if (this.singleRequestCache.isCached(datasetId)) {
      return this.singleRequestCache.get(datasetId);
    } else {
      let getURL = datasetUrl + '/' + datasetId;
      let dataset$ = this.httpClient.get<DatasetDto>(getURL).pipe(shareReplay());
      this.singleRequestCache.push(datasetId, dataset$);
      return dataset$.pipe(
        catchError(err => this.httpError.handleError(err))
      );
    }
  }

}

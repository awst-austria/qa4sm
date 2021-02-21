import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {DatasetDto} from './dataset.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environment';
import {shareReplay} from 'rxjs/operators';

const datasetUrl: string = environment.API_URL + 'api/dataset';
const CACHE_LIFETIME: number = 5 * 60 * 1000; // 5 minutes

@Injectable({
  providedIn: 'root'
})
export class DatasetService {

  datasets$: Observable<DatasetDto[]>;
  datasetsCreatedOn: Date;


  constructor(private httpClient: HttpClient) {
    this.datasets$ = this.httpClient.get<DatasetDto[]>(datasetUrl).pipe(shareReplay());
    this.datasetsCreatedOn = new Date();
  }

  getAllDatasets(): Observable<DatasetDto[]> {
    if (((new Date()).getTime() - this.datasetsCreatedOn.getTime()) > CACHE_LIFETIME) {
      this.datasets$ = this.httpClient.get<DatasetDto[]>(datasetUrl).pipe(shareReplay());
      this.datasetsCreatedOn = new Date();
    }
    return this.datasets$;
  }


}

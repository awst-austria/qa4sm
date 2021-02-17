import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {DatasetDto} from './dataset.dto';
import {Observable} from 'rxjs';
import {UserDto} from '../../core/services/auth/user.dto';
import {environment} from '../../../../environments/environment';

const datasetUrl: string = environment.API_URL + 'api/dataset';

@Injectable({
  providedIn: 'root'
})
export class DatasetService {
  datasets: DatasetDto[] = [];


  constructor(private httpClient: HttpClient) {
  }

  getAllDatasets(): Observable<DatasetDto[]> {
    return this.httpClient.get<DatasetDto[]>(datasetUrl);
  }


}

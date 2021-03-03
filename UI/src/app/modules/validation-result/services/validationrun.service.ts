import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ValidationrunDto} from './validationrun.dto';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environment';
import {DatasetDto} from '../../dataset/services/dataset.dto';
import {DatasetVersionDto} from '../../dataset/services/dataset-version.dto';
import {DatasetVariableDto} from '../../dataset/services/dataset-variable.dto';
import {DatasetService} from '../../dataset/services/dataset.service';
import {DatasetVersionService} from '../../dataset/services/dataset-version.service';
import {DatasetVariableService} from '../../dataset/services/dataset-variable.service';

const publishedValidationRunUrl: string = environment.API_URL + 'api/published-results';
const customValidationRunUrl: string = environment.API_URL + 'api/my-results';

@Injectable({
  providedIn: 'root'
})
export class ValidationrunService {

  customValidationrun$: Observable<ValidationrunDto[]>;
  publishedValidationrun$: Observable<ValidationrunDto[]>;

  constructor(private httpClient: HttpClient,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService) {
    this.publishedValidationrun$ = this.httpClient.get<ValidationrunDto[]>(publishedValidationRunUrl);
  }

  getPublishedValidationruns(): Observable<ValidationrunDto[]>{
    this.publishedValidationrun$ = this.httpClient.get<ValidationrunDto[]>(publishedValidationRunUrl);
    return  this.publishedValidationrun$;
  }

  getMyValidationruns(): Observable<ValidationrunDto[]>{
    this.customValidationrun$ = this.httpClient.get<ValidationrunDto[]>(customValidationRunUrl);
    return  this.customValidationrun$;
  }

  getAllDatasets(targetArray: DatasetDto[]) {
    this.datasetService.getAllDatasets().subscribe(datasets => {
      datasets.forEach(dataset => {
        targetArray.push(dataset);
      });
    });
  }

  getAllVersions(targetArray: DatasetVersionDto[]) {
    this.datasetVersionService.getAllVersions().subscribe(versions => {
      versions.forEach(version => {
        targetArray.push(version);
      });
    });
  }

  getAllVariables(targetArray: DatasetVariableDto[]) {
    this.datasetVariableService.getAllVariables().subscribe(variables => {
      variables.forEach(variable => {
        targetArray.push(variable);
      });
    });
  }

}

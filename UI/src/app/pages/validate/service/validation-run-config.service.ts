import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient, HttpParams} from '@angular/common/http';
import {ValidationRunConfigDto} from './validation-run-config-dto';
import {ValidationrunDto} from '../../../modules/core/services/validation-run/validationrun.dto';
import {BehaviorSubject, Observable} from 'rxjs';
import {ScalingMethodDto} from '../../../modules/scaling/components/scaling/scaling-methods.dto';
import {DatasetConfigModel} from '../dataset-config-model';
import {catchError} from 'rxjs/operators';
import {HttpErrorService} from '../../../modules/core/services/global/http-error.service';

const runValidationUrl: string = environment.API_URL + 'api/validation-configuration';
const getValidationConfigUrl: string = environment.API_URL + 'api/validation-configuration';
const getScalingMethodsUrl: string = environment.API_URL + 'api/scaling-methods';

/**
 * This service -together with its DTOs- responsible for submitting new validations
 */
@Injectable({
  providedIn: 'root'
})
export class ValidationRunConfigService {

  public listOfSelectedConfigs: BehaviorSubject<DatasetConfigModel[]>
    = new BehaviorSubject<DatasetConfigModel[]>([]);

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {

  }

  public startValidation(newValidationConfiguration: ValidationRunConfigDto, checkForExistingValidation: boolean):
    Observable<any> {
    const params = new HttpParams().set('check_for_existing_validation', String(checkForExistingValidation));
    return this.httpClient.post<ValidationrunDto>(runValidationUrl, newValidationConfiguration, {params})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  public getValidationConfig(validationRunId: string): Observable<ValidationRunConfigDto> {
    return this.httpClient.get<ValidationRunConfigDto>(getValidationConfigUrl + '/' + validationRunId)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  public getScalingMethods(): Observable<ScalingMethodDto[]> {
    return this.httpClient.get<ScalingMethodDto[]>(getScalingMethodsUrl)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  };

  readonly scalingMethods$ = this.httpClient.get<ScalingMethodDto[]>(getScalingMethodsUrl)
    .pipe(
      catchError(err => this.httpError.handleError(err))
    );

  public getInformationOnTheReference(isSpatialReference, isTemporalReference, isScalingReference): string {
    const listOfReference = [];
    if (isSpatialReference) {
      listOfReference.push('spatial');
    }
    if (isTemporalReference) {
      listOfReference.push('temporal');
    }
    if (isScalingReference) {
      listOfReference.push('scaling');
    }

    let information: string;
    listOfReference.length !== 0 ? information = ` (${listOfReference.join(', ')} reference)` : information = '';

    return information;
  };
}

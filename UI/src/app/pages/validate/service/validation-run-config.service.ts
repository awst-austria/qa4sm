import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient, HttpParams} from '@angular/common/http';
import {ValidationRunConfigDto} from './validation-run-config-dto';
import {ValidationrunDto} from '../../../modules/core/services/validation-run/validationrun.dto';
import {BehaviorSubject, Observable} from 'rxjs';
import {ScalingMethodDto} from '../../../modules/scaling/components/scaling/scaling-methods.dto';
import {DatasetConfigModel} from '../dataset-config-model';

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

  constructor(private httpClient: HttpClient) {

  }

  public startValidation(newValidationConfiguration: ValidationRunConfigDto, checkForExistingValidation: boolean): Observable<any> {
    const params = new HttpParams().set('check_for_existing_validation', String(checkForExistingValidation));
    return this.httpClient.post<ValidationrunDto>(runValidationUrl, newValidationConfiguration, {params});
  }

  public getValidationConfig(validationRunId: string): Observable<ValidationRunConfigDto> {
    return this.httpClient.get<ValidationRunConfigDto>(getValidationConfigUrl + '/' + validationRunId);
  }

  public getScalingMethods(): Observable<ScalingMethodDto[]> {
    return this.httpClient.get<ScalingMethodDto[]>(getScalingMethodsUrl);
  }


  public getInformationOnTheReference(isSpatialReference, isTemporalReference, isScalingReference, scalingMethod): string {
    const listOfReference = [];
    if (isSpatialReference) {
      listOfReference.push('spatial');
    }
    if (isTemporalReference) {
      listOfReference.push('temporal');
    }
    if (isScalingReference && scalingMethod !== 'none') {
      listOfReference.push('scaling');
    }

    let information: string;
    listOfReference.length !== 0 ? information = ` (${listOfReference.join(', ')} reference)` : information = '';

    return information;
  }
}

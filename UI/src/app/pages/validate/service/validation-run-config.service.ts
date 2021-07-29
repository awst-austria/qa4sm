import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient, HttpParams} from '@angular/common/http';
import {ValidationRunConfigDto} from './validation-run-config-dto';
import {ValidationrunDto} from '../../../modules/core/services/validation-run/validationrun.dto';
import {Observable} from 'rxjs';

const runValidationUrl: string = environment.API_URL + 'api/validation-configuration';
const getValidationConfigUrl: string = environment.API_URL + 'api/validation-configuration';

/**
 * This service -together with its DTOs- responsible for submitting new validations
 */
@Injectable({
  providedIn: 'root'
})
export class ValidationRunConfigService {

  constructor(private httpClient: HttpClient) {

  }

  public startValidation(newValidationConfiguration: ValidationRunConfigDto, checkForExistingValidation: boolean): Observable<any> {
    const params = new HttpParams().set('check_for_existing_validation', String(checkForExistingValidation));
    return this.httpClient.post<ValidationrunDto>(runValidationUrl, newValidationConfiguration, {params});
  }

  public getValidationConfig(validationRunId: string): Observable<ValidationRunConfigDto> {
    return this.httpClient.get<ValidationRunConfigDto>(getValidationConfigUrl + '/' + validationRunId);
  }
}

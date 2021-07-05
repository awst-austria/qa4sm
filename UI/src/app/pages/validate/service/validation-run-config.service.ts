import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
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

  public startValidation(newValidationConfiguration: ValidationRunConfigDto): Observable<ValidationrunDto> {
    return this.httpClient.post<ValidationrunDto>(runValidationUrl, newValidationConfiguration);
  }

  public getValidationConfig(validationRunId: string): Observable<ValidationRunConfigDto> {
    return this.httpClient.get<ValidationRunConfigDto>(getValidationConfigUrl + '/' + validationRunId);
  }
}

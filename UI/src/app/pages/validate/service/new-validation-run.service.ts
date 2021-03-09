import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {NewValidationRunDto} from './new-validation-run-dto';
import {ValidationrunDto} from '../../../modules/core/services/validation-run/validationrun.dto';
import {Observable} from 'rxjs';

const runValidationUrl: string = environment.API_URL + 'api/run-validation';

/**
 * This service -together with its DTOs- responsible for submitting new validations
 */
@Injectable({
  providedIn: 'root'
})
export class NewValidationRunService {

  constructor(private httpClient: HttpClient) {

  }

  public startValidation(newValidationConfiguration: NewValidationRunDto): Observable<ValidationrunDto> {
    return this.httpClient.post<ValidationrunDto>(runValidationUrl, newValidationConfiguration);
  }
}

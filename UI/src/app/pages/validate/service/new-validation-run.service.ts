import {Injectable} from '@angular/core';
import {environment} from '../../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {NewValidationRunDto} from './new-validation-run-dto';

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

  public startValidation(newValidationConfiguration: NewValidationRunDto) {
    console.log('sending: ', JSON.stringify(newValidationConfiguration));
    this.httpClient
      .post(runValidationUrl, newValidationConfiguration)
      .subscribe(
        data => {
          console.log(data);
        },
        error => {
          console.error(error);
        }
      );
  }
}

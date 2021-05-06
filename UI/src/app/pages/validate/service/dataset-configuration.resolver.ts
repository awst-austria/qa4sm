import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, Resolve, RouterStateSnapshot} from '@angular/router';
import {Observable} from 'rxjs';
import {DatasetConfigurationDto} from '../../../modules/validation-result/services/dataset-configuration.dto';
import {DatasetConfigurationService} from '../../../modules/validation-result/services/dataset-configuration.service';

@Injectable({
  providedIn: 'root'
})
export class DatasetConfigurationResolver implements Resolve<DatasetConfigurationDto[]> {
  constructor(private datasetConfigService: DatasetConfigurationService) {
  }
  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<DatasetConfigurationDto[]> {
    const validationId = route.paramMap.get('validationId');
    return this.datasetConfigService.getConfigByValidationrun(validationId);
  }
}

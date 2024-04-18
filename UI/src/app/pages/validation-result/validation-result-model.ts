import {ValidationrunDto} from '../../modules/core/services/validation-run/validationrun.dto';
import {DatasetConfigurationDto} from '../../modules/validation-result/services/dataset-configuration.dto';
import {Observable} from 'rxjs';

export class ValidationResultModel {
  constructor(public validationRun$: Observable<ValidationrunDto>,
              public datasetConfigs$: Observable<DatasetConfigurationDto[]>) {
  }


}

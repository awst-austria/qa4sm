import {ValidationrunDto} from '../../modules/core/services/validation-run/validationrun.dto';
import {DatasetConfigurationDto} from '../../modules/validation-result/services/dataset-configuration.dto';
import {Observable} from 'rxjs';


/**
 * Container for grouping two observables per validation run.
 * Used in comparison view where multiple validations are displayed simultaneously —
 * valResModels: ValidationResultModel[] allows iterating over validations
 * and passing both observables together to qa-validation-summary as a single input.
 */

export class ValidationResultModel {
  constructor(public validationRun$: Observable<ValidationrunDto>,
              public datasetConfigs$: Observable<DatasetConfigurationDto[]>) {
  }
}

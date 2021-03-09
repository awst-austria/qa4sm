import {ValidationrunDto} from '../../modules/core/services/validation-run/validationrun.dto';
import {DatasetConfigurationDto} from '../../modules/validation-result/services/dataset-configuration.dto';

export class ValidationResultModel {
  constructor(public validationRun: ValidationrunDto,
              public datasetConfigs: DatasetConfigurationDto[]) {
  }

  getComparedDatasets(): number {
    return this.datasetConfigs.length;
  }
}

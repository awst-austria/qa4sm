import {NewValRunDatasetConfigDto} from './new-val-run-dataset-config-dto';
import {NewValidationRunSpatialSubsettingDto} from './new-validation-run-spatial-subsetting-dto';
import {NewValidationRunValidationPeriodDto} from './new-validation-run-validation-period-dto';
import {NewValidationRunMetricDto} from './new-validation-run-metric-dto';

export class NewValidationRunDto {
  constructor(public dataset_configs: NewValRunDatasetConfigDto[],
              public reference_config: NewValRunDatasetConfigDto,
              public spatial_subsetting: NewValidationRunSpatialSubsettingDto,
              public validation_period: NewValidationRunValidationPeriodDto,
              public metrics: NewValidationRunMetricDto[]) {
  }
}

import {NewValRunDatasetConfigDto} from './new-val-run-dataset-config-dto';
import {NewValidationRunSpatialSubsettingDto} from './new-validation-run-spatial-subsetting-dto';

export class NewValidationRunDto {
  constructor(public dataset_configs: NewValRunDatasetConfigDto[],
              public reference_config: NewValRunDatasetConfigDto,
              public spatial_subsetting: NewValidationRunSpatialSubsettingDto) {
  }
}

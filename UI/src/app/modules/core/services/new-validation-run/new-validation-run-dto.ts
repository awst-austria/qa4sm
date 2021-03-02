import {NewValRunDatasetConfigDto} from './new-val-run-dataset-config-dto';

export class NewValidationRunDto {
  constructor(public dataset_configs: NewValRunDatasetConfigDto[],
              public reference_config: NewValRunDatasetConfigDto) {
  }
}

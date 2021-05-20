import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ValidationRunDatasetConfigDto} from './service/validation-run-config-dto';


export class DatasetConfigModel {
  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: FilterModel[],
              public parameterisedFilters: FilterModel[]) {
  }

  /**
   * This method prepares the DTO for starting the new validation
   */
  public toValRunDatasetConfigDto(): ValidationRunDatasetConfigDto {
    let enabledBasicFilters: number[] = [];
    this.basicFilters.forEach(filter => {
      if (filter.enabled) {
        enabledBasicFilters.push(filter.filterDto.id);
      }
    });

    let newValDatasetConfigDto: ValidationRunDatasetConfigDto = {
      dataset_id: this.datasetModel.selectedDataset.id,
      variable_id: this.datasetModel.selectedVariable.id,
      version_id: this.datasetModel.selectedVersion.id,
      basic_filters: enabledBasicFilters
    };

    return newValDatasetConfigDto;
  }
}

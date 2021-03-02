import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {NewValRunDatasetConfigDto} from '../../modules/core/services/new-validation-run/new-val-run-dataset-config-dto';


export class DatasetConfigModel {
  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: FilterModel[],
              public parameterisedFilters: FilterModel[]) {
  }

  /**
   * This method prepares the DTO for starting the new validation
   */
  public toNewValRunDatasetConfigDto(): NewValRunDatasetConfigDto {
    let enabledBasicFilters: number[] = [];
    this.basicFilters.forEach(filter => {
      if (filter.enabled) {
        enabledBasicFilters.push(filter.filterDto.id);
      }
    });

    let newValDatasetConfigDto = new NewValRunDatasetConfigDto(
      this.datasetModel.selectedDataset.id,
      this.datasetModel.selectedVersion.id,
      this.datasetModel.selectedVariable.id,
      enabledBasicFilters);
    return newValDatasetConfigDto;
  }
}

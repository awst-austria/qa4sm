import {
  DatasetComponentSelectionModel
} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ParametrisedFilterConfig, ValidationRunDatasetConfigDto} from './service/validation-run-config-dto';
import {BehaviorSubject} from 'rxjs';

export const ISMN_NETWORK_FILTER_ID = 18;
export const ISMN_DEPTH_FILTER_ID = 24;

export class DatasetConfigModel {

  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: FilterModel[],
              public ismnNetworkFilter$: BehaviorSubject<FilterModel>,
              public ismnDepthFilter$: BehaviorSubject<FilterModel>) {
  }

  /**
   * This method prepares the DTO for starting the new validation
   */
  public toValRunDatasetConfigDto(): ValidationRunDatasetConfigDto {
    const enabledBasicFilters: number[] = [];
    this.basicFilters.forEach(filter => {
      if (filter.enabled) {
        enabledBasicFilters.push(filter.filterDto.id);
      }
    });

    const parameterisedFilters: ParametrisedFilterConfig[] = [];
    if (this.ismnNetworkFilter$.value != null) {
      parameterisedFilters.push({id: ISMN_NETWORK_FILTER_ID, parameters: this.ismnNetworkFilter$.value.parameters$.value});
    }

    if (this.ismnDepthFilter$.value != null) {
      parameterisedFilters.push({id: ISMN_DEPTH_FILTER_ID, parameters: this.ismnDepthFilter$.value.parameters$.value});
    }

    const newValDatasetConfigDto: ValidationRunDatasetConfigDto = {
      dataset_id: this.datasetModel.selectedDataset.id,
      variable_id: this.datasetModel.selectedVariable.id,
      version_id: this.datasetModel.selectedVersion.id,
      basic_filters: enabledBasicFilters,
      parametrised_filters: parameterisedFilters
    };

    return newValDatasetConfigDto;
  }
}

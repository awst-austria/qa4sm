import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ParametrisedFilterConfig, ValidationRunDatasetConfigDto} from './service/validation-run-config-dto';
import {BehaviorSubject} from 'rxjs';
import {ThresholdFilterModel} from "../../modules/filter/components/threshold-filter/threshold-filter-model";

export const ISMN_NETWORK_FILTER_ID = 18;
export const ISMN_DEPTH_FILTER_ID = 24;

export class DatasetConfigModel {

  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: FilterModel[],
              public thresholdFilters: ThresholdFilterModel[],
              public ismnNetworkFilter$: BehaviorSubject<FilterModel>,
              public ismnDepthFilter$: BehaviorSubject<FilterModel>,
  ) {
  }

  /**
   * This method prepares the DTO for starting the new validation
   */
  public toValRunDatasetConfigDto(): ValidationRunDatasetConfigDto {
    const enabledBasicFilters: number[] = [];
    this.basicFilters.forEach(filter => {
      if (filter.enabled && !filter.filterDto.threshold) {
        enabledBasicFilters.push(filter.filterDto.id);
      }
    });

    const thresholdFilters: number[] = [];
    this.thresholdFilters.forEach(filter => {
      if (filter.filterDto.threshold) {
        thresholdFilters.push(filter.filterDto.id);
      }
    });

    const parameterisedFilters: ParametrisedFilterConfig[] = [];
    if (this.ismnNetworkFilter$.value != null) {
      parameterisedFilters.push({id: ISMN_NETWORK_FILTER_ID, parameters: this.ismnNetworkFilter$.value.parameters$.value});
    }

    if (this.ismnDepthFilter$.value != null) {
      parameterisedFilters.push({id: ISMN_DEPTH_FILTER_ID, parameters: this.ismnDepthFilter$.value.parameters$.value});
    }

    return {
      dataset_id: this.datasetModel.selectedDataset.id,
      variable_id: this.datasetModel.selectedVariable.id,
      version_id: this.datasetModel.selectedVersion.id,
      basic_filters: enabledBasicFilters,
      threshold_filters: thresholdFilters,
      parametrised_filters: parameterisedFilters
    };
  }
}

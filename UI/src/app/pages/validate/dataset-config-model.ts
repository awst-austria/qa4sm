import {
  DatasetComponentSelectionModel
} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ParametrisedFilterConfig, ValidationRunDatasetConfigDto} from './service/validation-run-config-dto';
import {BehaviorSubject} from 'rxjs';

export const ISMN_NETWORK_FILTER_ID = 18;
export const ISMN_DEPTH_FILTER_ID = 24;
export const SMOS_RFI_FILTER_ID = 34;
export const SMOS_CHI2_FILTER_ID = 35;
export const SMAP_L3_V9_VWC_FILTER_ID = 49;
export const SMAP_L3_STATIC_WATER_FILTER_ID = 50;

export class DatasetConfigModel {

  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: FilterModel[],
              public smosRfiFilter$: BehaviorSubject<FilterModel>,
              public smosChi2Filter$: BehaviorSubject<FilterModel>,
              public ismnNetworkFilter$: BehaviorSubject<FilterModel>,
              public ismnDepthFilter$: BehaviorSubject<FilterModel>,
              public spatialReference$: BehaviorSubject<boolean>,
              public temporalReference$: BehaviorSubject<boolean>,
              public scalingReference$: BehaviorSubject<boolean>,
              public vegetationWaterFilter$: BehaviorSubject<FilterModel>,
              public staticWaterFilter$: BehaviorSubject<FilterModel>,
              public highlighted$?: BehaviorSubject<boolean>,

  ) {
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

    if (this.smosRfiFilter$.value != null) {
      parameterisedFilters.push({id: SMOS_RFI_FILTER_ID, parameters: this.smosRfiFilter$.value.parameters$.value});
    }

    if (this.smosChi2Filter$.value != null) {
      parameterisedFilters.push({id: SMOS_CHI2_FILTER_ID, parameters: this.smosChi2Filter$.value.parameters$.value});
    }

    if (this.vegetationWaterFilter$.value != null) {
      parameterisedFilters.push({id: SMAP_L3_V9_VWC_FILTER_ID, parameters: this.vegetationWaterFilter$.value.parameters$.value});
    }

    if (this.staticWaterFilter$.value != null) {
      parameterisedFilters.push({id: SMAP_L3_STATIC_WATER_FILTER_ID, parameters: this.staticWaterFilter$.value.parameters$.value});
    }

    return {
      dataset_id: this.datasetModel.selectedDataset.id,
      variable_id: this.datasetModel.selectedVariable.id,
      version_id: this.datasetModel.selectedVersion.id,
      basic_filters: enabledBasicFilters,
      parametrised_filters: parameterisedFilters,
      is_spatial_reference: this.spatialReference$.value,
      is_temporal_reference: this.temporalReference$.value,
      is_scaling_reference: this.scalingReference$.value
    };
  }
}

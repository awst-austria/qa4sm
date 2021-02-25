import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';


export class DatasetConfigModel {
  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: FilterModel[],
              public parameterisedFilters: FilterModel[]) {
  }
}

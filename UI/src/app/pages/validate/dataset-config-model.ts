import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {BasicFilterModel} from '../../modules/filter/components/basic-filter/basic-filter-model';

export class DatasetConfigModel {
  constructor(public datasetModel: DatasetComponentSelectionModel,
              public basicFilters: BasicFilterModel[]) {
  }
}

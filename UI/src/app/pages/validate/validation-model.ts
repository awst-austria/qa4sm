import {DatasetConfigModel} from './dataset-config-model';
import {SpatialSubsetModel} from '../../modules/spatial-subset/components/spatial-subset/spatial-subset-model';

export class ValidationModel{
  // The reference configuration array should contain exactly one item.
  constructor(public datasetConfigurations:DatasetConfigModel[],
              public referenceConfigurations:DatasetConfigModel[],
              public spatialSubsetModel:SpatialSubsetModel) {
  }
}

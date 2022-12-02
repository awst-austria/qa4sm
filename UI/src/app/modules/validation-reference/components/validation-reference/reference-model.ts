import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';

export class ReferenceModel {
  constructor(public temporal: DatasetConfigModel,
              public spatial: DatasetConfigModel,
              public scaling: DatasetConfigModel
  ) {
  }
}

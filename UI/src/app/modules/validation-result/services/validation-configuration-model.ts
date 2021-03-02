import {DatasetConfigModel} from '../../../pages/validate/dataset-config-model';

export class ValidationConfigurationModel {
  // constructor(public datasetConfig: DatasetConfigModel[],
  //             public isReference: boolean[],
  // ){}
  constructor(public datasetConfig: DatasetConfigModel,
              public isReference: boolean,
  ){}
}

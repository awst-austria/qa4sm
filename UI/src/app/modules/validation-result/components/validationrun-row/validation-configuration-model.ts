import {DatasetRowModel} from './dataset-row.model';

export class ValidationConfigurationModel {
  constructor(public datasetConfig: DatasetRowModel,
              public isReference: boolean,
  ){}
}


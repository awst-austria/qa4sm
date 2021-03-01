import {ValidationrunDto} from './validationrun.dto';

export class ValidationConfigurationModel {
  constructor(public validationrunId: string,
              public datasets: number[],
              public datasetsVersions: number[],
              public datasetsVariables: number[],
              public refDataset: number,
              public refDatasetVersion: number,
              public refDatasetVariable: number
  ){}
}

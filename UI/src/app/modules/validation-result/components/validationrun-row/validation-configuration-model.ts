import {DatasetRowModel} from './dataset-row.model';
import {ValidationrunDto} from '../../services/validationrun.dto';


export class ValidationRunRowModel {
  constructor(public validationRun: ValidationrunDto,
              public datasetRows: DatasetRowModel[] = [],
              public referenceRow?: DatasetRowModel) {
  }
}

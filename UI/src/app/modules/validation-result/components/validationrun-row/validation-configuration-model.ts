import {DatasetRowModel} from './dataset-row.model';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';


export class ValidationRunRowModel {
  constructor(public validationRun: ValidationrunDto,
              public datasetRows: DatasetRowModel[] = [],
              public referenceRow?: DatasetRowModel) {
  }
}

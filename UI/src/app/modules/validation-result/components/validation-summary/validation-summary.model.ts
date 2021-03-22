import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetSummaryModel} from './dataset-summary.model';


export class ValidationSummaryModel {
  constructor(public validationRun: ValidationrunDto,
              public datasetSummary: DatasetSummaryModel[] = [],
              public referenceRow?: DatasetSummaryModel) {
  }
}

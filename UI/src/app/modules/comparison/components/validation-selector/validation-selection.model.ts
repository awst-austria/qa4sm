import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';

export class Validations2CompareModel {
  constructor(public validationRuns: ValidationrunDto[] = []) {
  }
}

import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';

export class Validations2CompareModel {
  // should mirror the comparison class in the qa4sm reader
  constructor(public selectedValidations: ValidationrunDto[] = [],
              public getIntersection: boolean,
              public multipleNonReference: boolean) {}
}

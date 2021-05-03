import {ValidationrunDto} from '../../core/services/validation-run/validationrun.dto';

export class ValidationSetDto {
  constructor(public validations: ValidationrunDto[],
              public length: number) {
  }
}

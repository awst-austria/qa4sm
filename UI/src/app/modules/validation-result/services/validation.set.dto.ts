import {ValidationrunDto} from './validationrun.dto';

export class ValidationSetDto {
  constructor(public validations: ValidationrunDto[],
              public length: number) {
  }
}

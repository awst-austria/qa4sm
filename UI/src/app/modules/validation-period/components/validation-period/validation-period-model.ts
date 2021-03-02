import {NewValidationRunValidationPeriodDto} from '../../../../pages/validate/service/new-validation-run-validation-period-dto';

export class ValidationPeriodModel {
  constructor(public intervalFrom?: Date,
              public intervalTo?: Date) {
  }

  public toNewValidationRunValidationPeriodDto(): NewValidationRunValidationPeriodDto {
    return new NewValidationRunValidationPeriodDto(this.intervalFrom, this.intervalTo);
  }
}

import {NewValidationRunAnomaliesDto} from '../../../core/services/new-validation-run/new-validation-run-anomalies-dto';

export class AnomaliesModel {
  constructor(public method: string,
              public description: string,
              public anomaliesFrom?: Date,
              public anomaliesTo?: Date) {
  }

  public toNewValidationRunAnomaliesDto(): NewValidationRunAnomaliesDto {
    return new NewValidationRunAnomaliesDto(this.method, this.anomaliesFrom, this.anomaliesTo);
  }
}

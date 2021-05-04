import {NewValidationRunAnomaliesDto} from '../../../../pages/validate/service/new-validation-run-anomalies-dto';

export class AnomaliesModel {
  constructor(public method: string,
              public description: string,
              public anomaliesFrom?: Date,
              public anomaliesTo?: Date,
              public selected?: boolean) {
  }

  public toNewValidationRunAnomaliesDto(): NewValidationRunAnomaliesDto {
    return new NewValidationRunAnomaliesDto(this.method, this.anomaliesFrom, this.anomaliesTo);
  }

  // public setAnomalies(method: string, anomaliesFrom: Date, anomaliesTo: Date): void{
  //   this.method = method;
  //   this.anomaliesFrom = anomaliesFrom;
  //   this.anomaliesTo = anomaliesTo;
  // }
}

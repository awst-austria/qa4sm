import {NewValidationRunMetricDto} from '../../../../pages/validate/service/new-validation-run-metric-dto';

export class MetricModel {
  constructor(public description: string,
              public helperText: string,
              public value: boolean,
              public enabled: boolean,
              public id: string) {
  }

  toNewValidationRunMetricDto(): NewValidationRunMetricDto {
    return new NewValidationRunMetricDto(this.id, this.value);
  }
}

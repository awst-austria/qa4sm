import {ValidationRunMetricConfigDto} from '../../../../pages/validate/service/validation-run-config-dto';

export class MetricModel {
  constructor(public description: string,
              public helperText: string,
              public value: boolean,
              public enabled: boolean,
              public id: string) {
  }

  toValidationRunMetricDto(): ValidationRunMetricConfigDto {
    return {id: this.id, value: this.value} as ValidationRunMetricConfigDto;
  }
}

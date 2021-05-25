import {ValidationRunMetricConfigDto} from '../../../../pages/validate/service/validation-run-config-dto';
import {BehaviorSubject} from 'rxjs';

export class MetricModel {
  constructor(public description: string,
              public helperText: string,
              public value$: BehaviorSubject<boolean>,
              public enabled: boolean,
              public id: string) {
  }

  toValidationRunMetricDto(): ValidationRunMetricConfigDto {
    return {id: this.id, value: this.value$.getValue()} as ValidationRunMetricConfigDto;
  }
}

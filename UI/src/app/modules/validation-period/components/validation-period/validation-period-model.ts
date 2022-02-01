import {BehaviorSubject} from 'rxjs';

export class ValidationPeriodModel {
  constructor(public intervalFrom$: BehaviorSubject<Date>,
              public intervalTo$: BehaviorSubject<Date>) {
  }
}

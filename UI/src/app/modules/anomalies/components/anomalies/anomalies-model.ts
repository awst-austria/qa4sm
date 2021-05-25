import {BehaviorSubject} from 'rxjs';

export class AnomaliesModel {
  constructor(public method$: BehaviorSubject<string>,
              public description: string,
              public anomaliesFrom$: BehaviorSubject<Date>,
              public anomaliesTo$: BehaviorSubject<Date>) {
  }
}

import {BehaviorSubject} from 'rxjs';
import {WritableSignal} from "@angular/core";

export class AnomaliesModel {
  constructor(public method$: BehaviorSubject<string>,
              public description: string,
              public anomaliesFrom: WritableSignal<Date>,
              public anomaliesTo: WritableSignal<Date>) {
  }
}

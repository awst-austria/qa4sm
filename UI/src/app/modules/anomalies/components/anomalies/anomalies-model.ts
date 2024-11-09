import {BehaviorSubject} from 'rxjs';
import {WritableSignal} from "@angular/core";

export class AnomaliesModel {
  constructor(public method$: BehaviorSubject<string>,
              public description: string,
              public anomaliesFrom: WritableSignal<number>,
              public anomaliesTo: WritableSignal<number>) {
  }
}

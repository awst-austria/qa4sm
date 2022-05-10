import {BehaviorSubject} from "rxjs";

export class TemporalMatchingModel {
  constructor(public size$: BehaviorSubject<number>,
              public description: string,) {
  }
}

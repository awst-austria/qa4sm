import {BehaviorSubject} from 'rxjs';

export class SpatialSubsetModel {
  constructor(public maxLat$: BehaviorSubject<number>,
              public maxLon$: BehaviorSubject<number>,
              public minLat$: BehaviorSubject<number>,
              public minLon$: BehaviorSubject<number>,
              public limited$: BehaviorSubject<boolean>,
              public maxLatLimit$?: BehaviorSubject<number>,
              public maxLonLimit$?: BehaviorSubject<number>,
              public minLatLimit$?: BehaviorSubject<number>,
              public minLonLimit$?: BehaviorSubject<number>) {
  }

}

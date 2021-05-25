import {ScalingToModel} from './scaling-to-model';
import {BehaviorSubject} from 'rxjs';

export class ScalingModel {
  constructor(public id: string,
              public description: string,
              public scaleTo$: BehaviorSubject<ScalingToModel>) {
  }

}

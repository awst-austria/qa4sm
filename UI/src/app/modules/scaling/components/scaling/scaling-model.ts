import {ScalingToModel} from './scaling-to-model';

export class ScalingModel {
  constructor(public id: string,
              public description: string,
              public scaleTo: ScalingToModel,
              public scaleToSelectorDisabled: boolean
  ) {
  }
}

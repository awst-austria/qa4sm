import {ScalingToModel} from './scaling-to-model';
import {NewValidationRunScalingDto} from '../../../../pages/validate/service/new-validation-run-scaling-dto';

export class ScalingModel {
  constructor(public id: string,
              public description: string,
              public scaleTo: ScalingToModel) {
  }

  public toNewValidationRunScalingDto(): NewValidationRunScalingDto {
    return new NewValidationRunScalingDto(this.id, this.scaleTo.id);
  }

}

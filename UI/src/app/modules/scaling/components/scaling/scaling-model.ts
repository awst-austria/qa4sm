import {ScalingToModel} from './scaling-to-model';
import {NewValidationRunScalingDto} from '../../../../pages/validate/service/new-validation-run-scaling-dto';

export class ScalingModel {
  constructor(public id: string,
              public description: string,
              public scaleTo: ScalingToModel,
              public selected?: boolean) {
  }

  public toNewValidationRunScalingDto(): NewValidationRunScalingDto {
    return new NewValidationRunScalingDto(this.id, this.scaleTo.id);
  }

  public setScalingMethod(method: string, scaleRef: string, scaleRefDesc: string): void{
    this.id = method;
    this.scaleTo = new ScalingToModel(scaleRef, scaleRefDesc);
    this.selected = true;
  }

}

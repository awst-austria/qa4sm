import {Component, Input, OnInit} from '@angular/core';
import {ScalingModel} from './scaling-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';
import {ScalingToModel} from './scaling-to-model';

export const SCALING_METHOD_NO_SCALING = 'none';
export const SCALING_METHOD_NO_SCALING_DESC = 'No scaling';

export const SCALING_METHOD_MIN_MAX = 'min_max';
export const SCALING_METHOD_MIN_MAX_DESC = 'Min/Max';

export const SCALING_METHOD_LIN_REG = 'linreg';
export const SCALING_METHOD_LIN_REG_DESC = 'Linear regression';

export const SCALING_METHOD_MEAN_STD = 'mean_std';
export const SCALING_METHOD_MEAN_STD_DESC = 'Mean/standard deviation';

export const SCALING_REFERENCE_REF = 'ref';
export const SCALING_REFERENCE_REF_DESC = 'Reference';
export const SCALING_REFERENCE_DATA = 'data';
export const SCALING_REFERENCE_DATA_DESC = 'Data';

export const SCALING_REFERENCE_DEFAULT = new ScalingToModel(SCALING_REFERENCE_REF, SCALING_REFERENCE_REF_DESC);
export const SCALING_METHOD_DEFAULT = new ScalingModel(SCALING_METHOD_NO_SCALING, SCALING_METHOD_NO_SCALING_DESC, SCALING_REFERENCE_DEFAULT);

export let SCALING_CHOICES = {};
SCALING_CHOICES[SCALING_METHOD_NO_SCALING] = SCALING_METHOD_NO_SCALING_DESC;
SCALING_CHOICES[SCALING_METHOD_MIN_MAX] = SCALING_METHOD_MIN_MAX_DESC;
SCALING_CHOICES[SCALING_METHOD_LIN_REG] = SCALING_METHOD_LIN_REG_DESC;
SCALING_CHOICES[SCALING_METHOD_MEAN_STD] = SCALING_METHOD_MEAN_STD_DESC;

export let SCALING_REFERENCE_CHOICES = {};
SCALING_REFERENCE_CHOICES[SCALING_REFERENCE_REF] = SCALING_REFERENCE_REF_DESC;
SCALING_REFERENCE_CHOICES[SCALING_REFERENCE_DATA] = SCALING_REFERENCE_DATA_DESC;


// export const SCALING_METHOD_LIN_CDF_MATCH='lin_cdf_match';
// export const SCALING_METHOD_CDF_MATCH='cdf_match';


@Component({
  selector: 'qa-scaling',
  templateUrl: './scaling.component.html',
  styleUrls: ['./scaling.component.scss']
})
export class ScalingComponent implements OnInit {

  readonly noScalingId = SCALING_METHOD_NO_SCALING;
  scalingModels: ScalingModel[] = [];
  selectedScalingModel: ScalingModel;

  scaleToModels: ScalingToModel[] = [];
  selectedScaleToModel: ScalingToModel;

  @Input() validationModel: ValidationModel;

  constructor() {
  }

  isScalingSelectorDisabled(): boolean {
    if (this.validationModel.datasetConfigurations.length > 1) {
      this.selectedScalingModel.scaleTo = SCALING_REFERENCE_DEFAULT;
      return true;
    } else {
      return false;
    }
  }

  ngOnInit(): void {
    this.prepareScalingModels();
    this.updateScalingModel();
    this.prepareScalingReferenceModels();
  }

  updateScalingModel() {
    this.validationModel.scalingModel.id = this.selectedScalingModel.id;
    this.validationModel.scalingModel.scaleTo = this.selectedScalingModel.scaleTo;
  }

  private prepareScalingReferenceModels() {
    this.scaleToModels.push(SCALING_REFERENCE_DEFAULT);
    this.scaleToModels.push(new ScalingToModel(SCALING_REFERENCE_DATA, SCALING_REFERENCE_DATA_DESC));
    this.selectedScaleToModel = this.scaleToModels[0];
  }

  private prepareScalingModels() {
    this.scalingModels.push(new ScalingModel(SCALING_METHOD_NO_SCALING, SCALING_METHOD_NO_SCALING_DESC, SCALING_REFERENCE_DEFAULT));
    this.scalingModels.push(new ScalingModel(SCALING_METHOD_MIN_MAX, SCALING_METHOD_MIN_MAX_DESC, SCALING_REFERENCE_DEFAULT));
    this.scalingModels.push(new ScalingModel(SCALING_METHOD_LIN_REG, SCALING_METHOD_LIN_REG_DESC, SCALING_REFERENCE_DEFAULT));
    this.scalingModels.push(new ScalingModel(SCALING_METHOD_MEAN_STD, SCALING_METHOD_MEAN_STD_DESC, SCALING_REFERENCE_DEFAULT));

    if (this.validationModel.scalingModel.selected){
      this.scalingModels.forEach(model => {
        if (model.id === this.validationModel.scalingModel.id){
          model.scaleTo = this.validationModel.scalingModel.scaleTo;
          this.selectedScalingModel = model;
        }
      });
      // this.selectedScalingModel = this.validationModel.scalingModel;
      // console.log('from scaling component', this.selectedScalingModel);
    } else{
      this.selectedScalingModel = this.scalingModels[0];
    }
  }

}

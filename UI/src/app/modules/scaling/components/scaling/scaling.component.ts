import {Component, Input, OnInit} from '@angular/core';
import {ScalingModel} from './scaling-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';
import {ScalingToModel} from './scaling-to-model';
import {BehaviorSubject} from 'rxjs';

export const SCALING_METHOD_NO_SCALING = 'none';
export const SCALING_METHOD_NO_SCALING_DESC = 'No scaling';

export const SCALING_METHOD_MIN_MAX = 'min_max';
export const SCALING_METHOD_MIN_MAX_DESC = 'Min/Max';

export const SCALING_METHOD_LIN_REG = 'linreg';
export const SCALING_METHOD_LIN_REG_DESC = 'Linear regression';

export const SCALING_METHOD_MEAN_STD = 'mean_std';
export const SCALING_METHOD_MEAN_STD_DESC = 'Mean/standard deviation';

export const SCALING_METHOD_CDF_MATCH = 'cdf_beta_match';
export const SCALING_METHOD_CDF_MATCH_DESC = 'Cumulative Distributions Functions (CDF) matching';

export const SCALING_REFERENCE_REF = 'ref';
export const SCALING_REFERENCE_REF_DESC = 'Reference';
export const SCALING_REFERENCE_DATA = 'data';
export const SCALING_REFERENCE_DATA_DESC = 'Data';

export const SCALING_REFERENCE_DEFAULT = new ScalingToModel(SCALING_REFERENCE_REF, SCALING_REFERENCE_REF_DESC);
export const SCALING_METHOD_DEFAULT = new ScalingModel(SCALING_METHOD_MEAN_STD, SCALING_METHOD_MEAN_STD_DESC,
  new BehaviorSubject<ScalingToModel>(SCALING_REFERENCE_DEFAULT));

export let SCALING_CHOICES = {};
SCALING_CHOICES[SCALING_METHOD_NO_SCALING] = SCALING_METHOD_NO_SCALING_DESC;
SCALING_CHOICES[SCALING_METHOD_MIN_MAX] = SCALING_METHOD_MIN_MAX_DESC;
SCALING_CHOICES[SCALING_METHOD_LIN_REG] = SCALING_METHOD_LIN_REG_DESC;
SCALING_CHOICES[SCALING_METHOD_MEAN_STD] = SCALING_METHOD_MEAN_STD_DESC;
SCALING_CHOICES[SCALING_METHOD_CDF_MATCH] = SCALING_METHOD_CDF_MATCH_DESC;


@Component({
  selector: 'qa-scaling',
  templateUrl: './scaling.component.html',
  styleUrls: ['./scaling.component.scss']
})
export class ScalingComponent implements OnInit {

  readonly noScalingId = SCALING_METHOD_NO_SCALING;
  scalingModels: ScalingModel[] =
    [ new ScalingModel(SCALING_METHOD_NO_SCALING, SCALING_METHOD_NO_SCALING_DESC,
       new BehaviorSubject<ScalingToModel>(SCALING_REFERENCE_DEFAULT)),
      new ScalingModel(SCALING_METHOD_MIN_MAX, SCALING_METHOD_MIN_MAX_DESC,
        new BehaviorSubject<ScalingToModel>(SCALING_REFERENCE_DEFAULT)),
      new ScalingModel(SCALING_METHOD_LIN_REG, SCALING_METHOD_LIN_REG_DESC,
        new BehaviorSubject<ScalingToModel>(SCALING_REFERENCE_DEFAULT)),
      new ScalingModel(SCALING_METHOD_MEAN_STD, SCALING_METHOD_MEAN_STD_DESC,
        new BehaviorSubject<ScalingToModel>(SCALING_REFERENCE_DEFAULT)),
      new ScalingModel(SCALING_METHOD_CDF_MATCH, SCALING_METHOD_CDF_MATCH_DESC,
        new BehaviorSubject<ScalingToModel>(SCALING_REFERENCE_DEFAULT))];
  selectedScalingModel: BehaviorSubject<ScalingModel>;

  scaleToModels: ScalingToModel[] = [];
  selectedScaleToModel$: BehaviorSubject<ScalingToModel>;

  @Input() validationModel: ValidationModel;

  constructor() {
  }

  isScalingSelectorDisabled(): boolean {
    if (this.validationModel.datasetConfigurations.length > 1) {
      this.selectedScaleToModel$.next(SCALING_REFERENCE_DEFAULT);
      return true;
    } else {
      return false;
    }
  }

  public setSelection(scalingMethodName: string, reference: string): void {
    this.scalingModels.forEach(scalingModel => {
      if (scalingModel.id === scalingMethodName) {
        this.scaleToModels.forEach(scaleToModel => {
          if (scaleToModel.id === reference) {
            scalingModel.scaleTo$.next(scaleToModel);
          }
        });
        this.selectedScalingModel.next(scalingModel);
      }
    });
    this.updateScalingModel();
  }

  ngOnInit(): void {
    this.selectedScalingModel = new BehaviorSubject<ScalingModel>(this.scalingModels.find(model => model.id === 'mean_std'));
    this.prepareScalingReferenceModels();
    this.updateScalingModel();
  }

  updateScalingModel(): void{
    this.validationModel.scalingModel.id = this.selectedScalingModel.getValue().id;
    this.validationModel.scalingModel.scaleTo$.next(this.selectedScaleToModel$.getValue());
  }

  private prepareScalingReferenceModels(): void{
    this.scaleToModels.push(SCALING_REFERENCE_DEFAULT);
    this.scaleToModels.push(new ScalingToModel(SCALING_REFERENCE_DATA, SCALING_REFERENCE_DATA_DESC));
    this.selectedScaleToModel$ = new BehaviorSubject<ScalingToModel>(this.scaleToModels[0]);
  }

}

import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ValidationModel} from '../../../../pages/validate/validation-model';
import {BehaviorSubject} from 'rxjs';
import {ValidationRunConfigService} from '../../../../pages/validate/service/validation-run-config.service';
import {ScalingMethodDto} from './scaling-methods.dto';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';


@Component({
  selector: 'qa-scaling',
  templateUrl: './scaling.component.html',
  styleUrls: ['./scaling.component.scss']
})
export class ScalingComponent implements OnInit {

  @Input() validationModel: ValidationModel;
  @Output() hoverOverDataset = new EventEmitter<any>();

  selectedScaleToModel$: BehaviorSubject<DatasetConfigModel> = new BehaviorSubject<DatasetConfigModel>(null);
  selectedScaleToModel: DatasetConfigModel;


  scalingMethods: ScalingMethodDto[];
  selectedScalingMethod$: BehaviorSubject<ScalingMethodDto> = new BehaviorSubject<ScalingMethodDto>(null);

  constructor(private validationConfigService: ValidationRunConfigService) {
  }
  ngOnInit(): void {
    // prepare method choices
    this.validationConfigService.scalingMethods$.subscribe(methods => {
      this.scalingMethods = methods;
      this.selectedScalingMethod$.next(methods.find(method => method.method === 'none'));
      this.setScalingMethod();
    });
  }

  setScalingMethod(): void{
    this.validationModel.scalingMethod.methodName = this.selectedScalingMethod$.getValue().method;
    this.validationModel.scalingMethod.methodDescription = this.selectedScalingMethod$.getValue().description;
  }
  updateScalingMethod(): void{
    this.setScalingMethod();

    if (this.selectedScalingMethod$.getValue().method === 'none'){
      this.selectedScaleToModel$.next(null);
      this.selectedScaleToModel ? this.updateScaleTo(true) : this.updateScaleTo();
    } else {
      if (!this.selectedScaleToModel){
        this.selectedScaleToModel$.next(this.validationModel.datasetConfigurations[0]);
        this.updateScaleTo();
      }
    }
  }

  updateScaleTo(clearSelected = false): void{
    if (clearSelected){
      this.selectedScaleToModel.scalingReference$.next(false);
    }

    this.selectedScaleToModel = this.selectedScaleToModel$.getValue();
    if (this.selectedScaleToModel){
      this.selectedScaleToModel.scalingReference$.next(true);
    }
  }

  onHoverOverDataset(item, highlight): void{
    this.hoverOverDataset.emit({hoveredDataset: item, highlight});
  }

  verifyScaleToModel(): BehaviorSubject<DatasetConfigModel>{
    this.selectedScaleToModel = this.validationModel.datasetConfigurations
      .find(datasetConfig => datasetConfig.scalingReference$.getValue());
    this.selectedScaleToModel$.next(this.selectedScaleToModel);
    return this.selectedScaleToModel$;
  }

  public setSelection(scalingMethodName: string, reference: DatasetConfigModel): void {

    this.validationConfigService.scalingMethods$.subscribe(methods => {
      methods.forEach(scalingMethod => {
        if (scalingMethod.method === scalingMethodName) {
          this.selectedScalingMethod$.next(scalingMethod);
        }
      });
      this.updateScalingMethod();
    });
    this.selectedScaleToModel$.next(reference);
    this.updateScaleTo();
  }

}

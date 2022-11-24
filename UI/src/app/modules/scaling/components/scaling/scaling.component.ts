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
    // prepare reference choices
    this.selectedScaleToModel = this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig.scalingReference);
    this.selectedScaleToModel$.next(this.selectedScaleToModel);


    // prepare method choices
    this.validationConfigService.getScalingMethods().subscribe(methods => {
      this.scalingMethods = methods;
      this.selectedScalingMethod$.next(methods.find(method => method.method === 'none'));
    });
  }

  updateScalingMethod(): void{
    this.validationModel.scalingMethod.methodName = this.selectedScalingMethod$.getValue().method;
    this.validationModel.scalingMethod.methodDescription = this.selectedScalingMethod$.getValue().description;
  }

  updateScaleTo(): void{
    this.selectedScaleToModel.scalingReference.next(false);
    this.selectedScaleToModel = this.selectedScaleToModel$.getValue();
    this.selectedScaleToModel.scalingReference.next(true);
  }

  onHoverOverDataset(item, highlight): void{
    this.hoverOverDataset.emit({hoveredDataset: item, highlight});
  }

}

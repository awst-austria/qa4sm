import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';

@Component({
  selector: 'qa-validation-reference',
  templateUrl: './validation-reference.component.html',
  styleUrls: ['./validation-reference.component.scss']
})
export class ValidationReferenceComponent implements OnInit {

  datasets$: Observable<any> = new Observable();

  @Input() validationModel: ValidationModel;
  @Input() referenceType: string;
  @Output() hoverOverDataset = new EventEmitter<any>();

  chosenDatasets$: BehaviorSubject<DatasetConfigModel[]> = new BehaviorSubject<DatasetConfigModel[]>(null);
  selectionModel$: BehaviorSubject<DatasetConfigModel> = new BehaviorSubject<DatasetConfigModel>(null);
  selectedValue: DatasetConfigModel;
  constructor() {
  }

  ngOnInit(): void {
    this.selectedValue = this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig[this.referenceType].getValue());
    this.selectionModel$.next(this.selectedValue);
  }

  onDatasetChange(reference = null): void {
    if (!reference){
      this.selectedValue[this.referenceType].next(false);
    }
    this.selectedValue = this.selectionModel$.getValue();
    this.selectedValue[this.referenceType].next(true);
  }

  onHoverOverDataset(item, highlight): void{
    this.hoverOverDataset.emit({hoveredDataset: item, highlight});
  }

  verifyOptions(): BehaviorSubject<DatasetConfigModel[]>{
    this.chosenDatasets$.next(this.validationModel.datasetConfigurations);
    if (this.referenceType === 'spatialReference$'){
      const listOfISMNDatasets = this.validationModel.datasetConfigurations.filter(dataset =>
        dataset.datasetModel.selectedDataset?.short_name === 'ISMN');
      const listOfServiceDatasets = this.validationModel.datasetConfigurations.filter(dataset =>
      !dataset.datasetModel.selectedDataset?.user);
      if (listOfISMNDatasets.length !== 0){
        this.chosenDatasets$.next(listOfISMNDatasets);
      } else if (listOfServiceDatasets.length < this.validationModel.datasetConfigurations.length) {
        this.chosenDatasets$.next(listOfServiceDatasets);
      }
    }
    return this.chosenDatasets$;
  }

  verifyChosenValue(): BehaviorSubject<DatasetConfigModel>{
    this.selectedValue = this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig[this.referenceType].getValue());
    this.selectionModel$.next(this.selectedValue);
    return this.selectionModel$;
  }

  setReference(reference: DatasetConfigModel): void{
    this.selectionModel$.next(reference);
    this.onDatasetChange(reference);
  }

}

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { DatasetConfigModel } from '../../../../pages/validate/dataset-config-model';
import { ValidationModel } from '../../../../pages/validate/validation-model';

@Component({
  selector: 'qa-validation-reference',
  templateUrl: './validation-reference.component.html',
  styleUrls: ['./validation-reference.component.scss']
})
export class ValidationReferenceComponent implements OnInit {

  @Input() validationModel: ValidationModel;
  @Input() referenceType: string;
  @Output() hoverOverDataset = new EventEmitter<any>();

  selectionModel$: BehaviorSubject<DatasetConfigModel> = new BehaviorSubject<DatasetConfigModel>(null);
  selectedValue: DatasetConfigModel;
  constructor() {
  }

  ngOnInit(): void {
    this.selectedValue = this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig[this.referenceType].getValue());
    this.selectionModel$.next(this.selectedValue);
  }

  onDatasetChange(reference = null): void {
    if (!reference) {
      this.selectedValue[this.referenceType].next(false);
    }
    this.selectedValue = this.selectionModel$.getValue();
    this.selectedValue[this.referenceType].next(true);
  }

  onHoverOverDataset(item, highlight): void {
    this.hoverOverDataset.emit({ hoveredDataset: item, highlight });
  }

  verifyOptions(): BehaviorSubject<DatasetConfigModel[]> {
    const availableDatasets = this.validationModel.datasetConfigurations;
    if (this.referenceType === 'spatialReference$') {
      const listOfISMNDatasets = availableDatasets.filter(dataset => dataset.datasetModel.selectedDataset.short_name === 'ISMN');
      if (listOfISMNDatasets.length) {
        return new BehaviorSubject(listOfISMNDatasets);
      }
    }
    return new BehaviorSubject(availableDatasets);
  }

  verifyChosenValue(): Observable<DatasetConfigModel> {
    this.selectedValue = this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig[this.referenceType].getValue());
    this.selectionModel$.next(this.selectedValue);
    return this.selectionModel$;
  }

  setReference(reference: DatasetConfigModel): void {
    this.selectionModel$.next(reference);
    this.onDatasetChange(reference);
  }

}

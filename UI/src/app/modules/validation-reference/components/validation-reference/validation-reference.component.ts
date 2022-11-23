import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';

@Component({
  selector: 'qa-validation-reference',
  templateUrl: './validation-reference.component.html',
  styleUrls: ['./validation-reference.component.scss']
})
export class ValidationReferenceComponent implements OnInit {

  datasets$: Observable<any> = new Observable();

  @Input() chosenDatasets$: BehaviorSubject<DatasetConfigModel[]>;
  @Input() selectionModel: DatasetConfigModel;
  @Output() changeDataset = new EventEmitter<DatasetConfigModel>();
  @Output() hoverOverDataset = new EventEmitter<any>();

  constructor() {
  }

  ngOnInit(): void {
  }

  onDatasetChange(): void {
    this.changeDataset.emit(this.selectionModel);
  }

  onHoverOverDataset(item, highlight): void{
    this.hoverOverDataset.emit({hoveredDataset: item, highlight});
  }

}

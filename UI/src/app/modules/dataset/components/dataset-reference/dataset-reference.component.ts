import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {DatasetComponentSelectionModel} from '../dataset/dataset-component-selection-model';
import {Observable} from 'rxjs';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';

@Component({
  selector: 'qa-dataset-reference',
  templateUrl: './dataset-reference.component.html',
  styleUrls: ['./dataset-reference.component.scss']
})
export class DatasetReferenceComponent implements OnInit {

  datasets$: Observable<DatasetDto[]>;
  @Input() selectionModel: DatasetComponentSelectionModel;
  @Output() changeDataset = new EventEmitter<DatasetComponentSelectionModel>();
  constructor() { }

  ngOnInit(): void {
  }

  onDatasetChange(): void{
    console.log('I changed something');
  }

}

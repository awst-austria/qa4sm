import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {DatasetService} from '../../services/dataset.service';
import {DatasetDto} from '../../services/dataset.dto';
import {DatasetSelection} from './dataset-selection';
import {Observable} from 'rxjs';


@Component({
  selector: 'qa-dataset',
  templateUrl: './dataset.component.html',
  styleUrls: ['./dataset.component.scss']
})
export class DatasetComponent implements OnInit {

  @Input() datasets$: Observable<DatasetDto[]>;
  datasets: DatasetDto[] = [];

  @Input() datasetSelection: DatasetSelection;
  @Input() removable: boolean = false;
  @Output() removeDataset = new EventEmitter<DatasetSelection>();

  selectedDataset: DatasetDto;


  constructor(private datasetService: DatasetService) {
  }

  ngOnInit(): void {
    this.datasetService.getAllDatasets().subscribe(
      datasets => this.datasets = datasets
    );
  }

  onDatasetChange() {
    this.datasetSelection.datasetId = this.selectedDataset.id;
    this.datasetSelection.datasetName = this.selectedDataset.pretty_name;
  }

  onRemoveDataset() {
    this.removeDataset.emit(this.datasetSelection);
  }


}

import {Component, Input, OnInit, Output, EventEmitter, Directive, AfterViewInit} from '@angular/core';
import {DatasetService} from '../../services/dataset.service';
import {DatasetDto} from '../../services/dataset.dto';
import {DatasetSelection} from './dataset-selection';


@Component({
  selector: 'qa-dataset',
  templateUrl: './dataset.component.html',
  styleUrls: ['./dataset.component.scss']
})
export class DatasetComponent implements OnInit,AfterViewInit {
  datasets: DatasetDto[] = [];


  // @ts-ignore
  @Input() datasetSelectorId: number;
  @Output() datasetSelectionChange = new EventEmitter<DatasetSelection>();

  // @ts-ignore
  selectedDataset: DatasetDto;

  datasetSelection: DatasetSelection | undefined;

  constructor(private datasetService: DatasetService) {

  }

  ngAfterViewInit(): void {
        console.log('after view')
    }

  ngOnInit(): void {
    this.datasetService.getAllDatasets().subscribe(
      datasets => this.datasets = datasets
    );
    this.datasetSelection = new DatasetSelection(this.datasetSelectorId,
      'asd', 1, 1, 1);
  }

  onDatasetChange() {
    // @ts-ignore
    this.datasetSelection.id = this.selectedDataset.id;
    // @ts-ignore
    this.datasetSelection.datasetName = this.selectedDataset.pretty_name;
    this.datasetSelectionChange.emit(this.datasetSelection);
  }



}

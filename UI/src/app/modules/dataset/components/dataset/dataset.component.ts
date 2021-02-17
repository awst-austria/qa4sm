import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../services/dataset.service';
import {DatasetDto} from '../../services/dataset.dto';

@Component({
  selector: 'qa-dataset',
  templateUrl: './dataset.component.html',
  styleUrls: ['./dataset.component.scss']
})
export class DatasetComponent implements OnInit {
  datasets: DatasetDto[] = [];
  selectedDataset: DatasetDto | undefined;

  constructor(private datasetService: DatasetService) {
  }

  ngOnInit(): void {
    this.datasetService.getAllDatasets().subscribe(
      datasets => this.datasets = datasets
    );
  }

  onDatasetChange(){
    console.log('Selected dataset: ',this.selectedDataset);
  }

}

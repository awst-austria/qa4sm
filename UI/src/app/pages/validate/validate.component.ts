import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetSelection} from '../../modules/dataset/components/dataset/dataset-selection';

const MAX_DATASETS_FOR_VALIDATION = 5;  //TODO: this should com from either config file or the database

@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss']
})
export class ValidateComponent implements OnInit {
  selectedDatasets: DatasetSelection[] = [];
  selectedReference: DatasetSelection[] = [];

  constructor(private datasetService: DatasetService) {
    this.selectedDatasets.push(new DatasetSelection(
      '[Select a dataset]', -1, -1, -1));
    this.selectedReference.push(new DatasetSelection(
      '[Select a dataset]', -1, -1, -1));
  }


  removeDataset(selection: DatasetSelection) {
    let toBeRemoved = this.selectedDatasets.indexOf(selection);
    if (toBeRemoved > -1) {
      this.selectedDatasets.splice(toBeRemoved, 1);
    }
  }

  addDataset() {

  }

  ngOnInit(): void {

    this.datasetService.getAllDatasets().subscribe(datasets => {
      if (datasets.length > 0) {
        this.selectedReference.push(new DatasetSelection(
          datasets[1].pretty_name, datasets[1].id, 0, 0));
      }
    });
    this.addDataset();
  }

  addDatasetButtonDisabled(): boolean {
    return this.selectedDatasets.length >= MAX_DATASETS_FOR_VALIDATION;
  }

}

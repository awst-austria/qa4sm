import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetSelection} from '../../modules/dataset/components/dataset/dataset-selection';


@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss']
})
export class ValidateComponent implements OnInit {
  selectedDatasets: DatasetSelection[] = [];

  constructor(private datasetService: DatasetService) {


  }

  updateDatasetSelection(selection: DatasetSelection) {
    console.log('update', selection);

    this.selectedDatasets[selection.idx].datasetName = selection.datasetName;
    console.log(this.selectedDatasets);
  }

  ngOnInit(): void {
    this.datasetService.getAllDatasets().subscribe(datasets => {
      datasets.forEach(dataset => this.selectedDatasets.push(new DatasetSelection(this.selectedDatasets.length,
        dataset.pretty_name, dataset.id, 0, 0)));
    });
  }

}

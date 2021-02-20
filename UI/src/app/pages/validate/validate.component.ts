import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetSelection} from '../../modules/dataset/components/dataset/dataset-selection';
import {RndGenService} from '../../modules/core/services/rnd-gen.service';


@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss']
})
export class ValidateComponent implements OnInit {
  selectedDatasets: DatasetSelection[] = [];

  constructor(private datasetService: DatasetService) {
  }


  removeDataset(selection: DatasetSelection) {
    let toBeRemoved = this.selectedDatasets.indexOf(selection);
    if (toBeRemoved > -1) {
      this.selectedDatasets.splice(toBeRemoved, 1);
    }
  }

  ngOnInit(): void {
    this.datasetService.getAllDatasets().subscribe(datasets => {
      if (datasets.length > 0) {
        this.selectedDatasets.push(new DatasetSelection(
          datasets[0].pretty_name, datasets[0].id, 0, 0));
      }
    });
  }

}

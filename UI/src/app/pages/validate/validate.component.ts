import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {DatasetVersionService} from '../../modules/dataset/services/dataset-version.service';
import {DatasetVariableService} from '../../modules/dataset/services/dataset-variable.service';

const MAX_DATASETS_FOR_VALIDATION = 5;  //TODO: this should come from either config file or the database

@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidateComponent implements OnInit {
  selectedDatasets: DatasetComponentSelectionModel[] = [];
  selectedReference: DatasetComponentSelectionModel[] = [];

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService) {

  }


  removeDataset(selection: DatasetComponentSelectionModel) {
    let toBeRemoved = this.selectedDatasets.indexOf(selection);
    if (toBeRemoved > -1) {
      this.selectedDatasets.splice(toBeRemoved, 1);
    }
  }

  addDatasetToValidate() {
    this.addDataset(this.selectedDatasets);
  }

  addReferenceDataset() {
    this.addDataset(this.selectedReference);
  }

  private addDataset(targetArray: DatasetComponentSelectionModel[]) {
    this.datasetService.getAllDatasets().subscribe(datasets => {
      let model = new DatasetComponentSelectionModel(datasets[0], null, null);
      this.versionService.getVersionsByDataset(model.selectedDataset.id).subscribe(versions => {
        model.selectedVersion = versions[0];
        this.variableService.getVariablesByDataset(model.selectedDataset.id).subscribe(variables => {
          model.selectedVariable = variables[0];
          targetArray.push(model);
        });
      });
    });
  }

  ngOnInit(): void {
    this.addDatasetToValidate();
    this.addReferenceDataset();
  }

  addDatasetButtonDisabled(): boolean {
    return this.selectedDatasets.length >= MAX_DATASETS_FOR_VALIDATION;
  }

}

import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {DatasetVersionService} from '../../modules/dataset/services/dataset-version.service';
import {DatasetVariableService} from '../../modules/dataset/services/dataset-variable.service';
import {DatasetConfigModel} from './dataset-config-model';
import {FilterService} from '../../modules/filter/services/filter.service';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';

const MAX_DATASETS_FOR_VALIDATION = 5;  //TODO: this should come from either config file or the database

@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidateComponent implements OnInit {
  datasetConfigurations: DatasetConfigModel[] = [];
  referenceConfiguration: DatasetConfigModel[] = []; // this array will always contain exactly 1 element


  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService,
              private filterService: FilterService) {

  }


  addDatasetToValidate() {
    this.addDataset(this.datasetConfigurations);
  }

  addReferenceDataset() {
    this.addDataset(this.referenceConfiguration);
  }

  private addDataset(targetArray: DatasetConfigModel[]) {

    let model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
    targetArray.push(model);
    //get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      model.datasetModel.selectedDataset = datasets[0];

      //then get all versions for the first dataset in the result list
      this.versionService.getVersionsByDataset(model.datasetModel.selectedDataset.id).subscribe(versions => {
        model.datasetModel.selectedVersion = versions[0];
      });

      // in the same time get the variables too
      this.variableService.getVariablesByDataset(model.datasetModel.selectedDataset.id).subscribe(variables => {
        model.datasetModel.selectedVariable = variables[0];
      });

      //and the filters
      this.updateDatasetConfigFilters(model);
    });
  }

  private updateDatasetConfigFilters(model: DatasetConfigModel) {
    this.filterService.getFilterByDatasetId(model.datasetModel.selectedDataset.id).subscribe(filters => {
      model.basicFilters = [];
      model.parameterisedFilters = [];
      filters.forEach(filter => {
        if (filter.parameterised) {
          model.parameterisedFilters.push(new FilterModel(filter, false, filter.default_parameter));
        } else {
          model.basicFilters.push(new FilterModel(filter, false, null));
        }
      });
    });
  }

  removeDataset(configModel: DatasetConfigModel) {
    let toBeRemoved = this.datasetConfigurations.indexOf(configModel);
    if (toBeRemoved > -1) {
      this.datasetConfigurations.splice(toBeRemoved, 1);
    }
  }

  onDatasetChange(datasetConfig: DatasetComponentSelectionModel) {
    this.datasetConfigurations.forEach(config => {
      if (config.datasetModel == datasetConfig) {
        this.updateDatasetConfigFilters(config);
      }
    });
  }

  onReferenceChange() {
    this.updateDatasetConfigFilters(this.referenceConfiguration[0]);
  }

  ngOnInit(): void {
    this.addDatasetToValidate();
    this.addReferenceDataset();
  }

  addDatasetButtonDisabled(): boolean {
    return this.datasetConfigurations.length >= MAX_DATASETS_FOR_VALIDATION;
  }
}

import {Component, OnInit} from '@angular/core';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {DatasetVersionService} from '../../modules/dataset/services/dataset-version.service';
import {DatasetVariableService} from '../../modules/dataset/services/dataset-variable.service';
import {DatasetConfigModel} from './dataset-config-model';
import {FilterService} from '../../modules/filter/services/filter.service';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ValidationModel} from './validation-model';
import {SpatialSubsetModel} from '../../modules/spatial-subset/components/spatial-subset/spatial-subset-model';
import {ValidationPeriodModel} from '../../modules/validation-period/components/validation-period/validation-period-model';
import {AnomaliesModel} from '../../modules/anomalies/components/anomalies/anomalies-model';
import {ANOMALIES_NONE, ANOMALIES_NONE_DESC} from '../../modules/anomalies/components/anomalies/anomalies.component';
import {SCALING_METHOD_DEFAULT} from '../../modules/scaling/components/scaling/scaling.component';
import {NewValidationRunDto} from '../../modules/core/services/new-validation-run/new-validation-run-dto';
import {NewValRunDatasetConfigDto} from '../../modules/core/services/new-validation-run/new-val-run-dataset-config-dto';
import {NewValidationRunService} from '../../modules/core/services/new-validation-run/new-validation-run.service';

const MAX_DATASETS_FOR_VALIDATION = 5;  //TODO: this should come from either config file or the database

@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidateComponent implements OnInit {
  // datasetConfigurations: DatasetConfigModel[] = [];
  // referenceConfiguration: DatasetConfigModel[] = []; // this array will always contain exactly 1 element

  validationModel: ValidationModel = new ValidationModel(
    [],
    [],
    new SpatialSubsetModel(),
    new ValidationPeriodModel(),
    [],
    new AnomaliesModel(ANOMALIES_NONE, ANOMALIES_NONE_DESC),
    SCALING_METHOD_DEFAULT);

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService,
              private filterService: FilterService,
              private newValidationService: NewValidationRunService) {

  }

  ngOnInit(): void {
    this.addDatasetToValidate();
    this.addReferenceDataset();
  }

  addDatasetToValidate() {
    this.addDataset(this.validationModel.datasetConfigurations);
  }

  addReferenceDataset() {
    this.addDataset(this.validationModel.referenceConfigurations);
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
    let toBeRemoved = this.validationModel.datasetConfigurations.indexOf(configModel);
    if (toBeRemoved > -1) {
      this.validationModel.datasetConfigurations.splice(toBeRemoved, 1);
    }
  }

  onDatasetChange(datasetConfig: DatasetComponentSelectionModel) {
    this.validationModel.datasetConfigurations.forEach(config => {
      if (config.datasetModel == datasetConfig) {
        this.updateDatasetConfigFilters(config);
      }
    });
  }

  onReferenceChange() {
    this.updateDatasetConfigFilters(this.validationModel.referenceConfigurations[0]);
  }


  addDatasetButtonDisabled(): boolean {
    return this.validationModel.datasetConfigurations.length >= MAX_DATASETS_FOR_VALIDATION;
  }

  public startValidation() {
    //debug
    console.log(JSON.stringify(this.validationModel));

    //prepare the dataset dtos (dataset, version, variable and filter settings)
    let datasets: NewValRunDatasetConfigDto[] = [];
    this.validationModel.datasetConfigurations.forEach(datasetConfig => {
      datasets.push(datasetConfig.toNewValRunDatasetConfigDto());
    });

    //prepare the reference dto  (dataset, version, variable and filter settings)
    let reference = this.validationModel.referenceConfigurations[0].toNewValRunDatasetConfigDto();
    let newValidationDto = new NewValidationRunDto(datasets, reference);
    this.newValidationService.startValidation(newValidationDto);
  }
}

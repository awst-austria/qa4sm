import {AfterViewInit, Component, OnInit, ViewChild} from '@angular/core';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {DatasetComponentSelectionModel} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../modules/core/services/dataset/dataset-variable.service';
import {DatasetConfigModel} from './dataset-config-model';
import {FilterService} from '../../modules/core/services/filter/filter.service';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ValidationModel} from './validation-model';
import {SpatialSubsetModel} from '../../modules/spatial-subset/components/spatial-subset/spatial-subset-model';
import {ValidationPeriodModel} from '../../modules/validation-period/components/validation-period/validation-period-model';
import {AnomaliesModel} from '../../modules/anomalies/components/anomalies/anomalies-model';
import {ANOMALIES_NONE, ANOMALIES_NONE_DESC} from '../../modules/anomalies/components/anomalies/anomalies.component';
import {SCALING_METHOD_DEFAULT} from '../../modules/scaling/components/scaling/scaling.component';
import {ValidationRunConfigDto, ValidationRunDatasetConfigDto, ValidationRunMetricConfigDto} from './service/validation-run-config-dto';
import {ValidationRunConfigService} from './service/validation-run-config.service';

import {ToastService} from '../../modules/core/services/toast/toast.service';
import {ActivatedRoute, Router} from '@angular/router';
import {BehaviorSubject} from 'rxjs';
import {MapComponent} from '../../modules/map/components/map/map.component';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';


const MAX_DATASETS_FOR_VALIDATION = 5;  //TODO: this should come from either config file or the database

@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidateComponent implements OnInit, AfterViewInit {
  @ViewChild(MapComponent) child: MapComponent;

  mapVisible: BehaviorSubject<Boolean> = new BehaviorSubject<Boolean>(false);
  validationModel: ValidationModel = new ValidationModel(
    [],
    [],
    new SpatialSubsetModel(
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null)),
    new ValidationPeriodModel(),
    [],
    new AnomaliesModel(ANOMALIES_NONE, ANOMALIES_NONE_DESC),
    SCALING_METHOD_DEFAULT);
  validationStart: Date = new Date('1978-01-01');
  validationEnd: Date = new Date();

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService,
              private filterService: FilterService,
              private validationConfigService: ValidationRunConfigService,
              private validationRunService: ValidationrunService,
              private toastService: ToastService,
              private router: Router,
              private route: ActivatedRoute) {
  }

  ngAfterViewInit(): void {
    // child init could be done here
  }

  ngOnInit(): void {

    this.route.queryParams.subscribe(params => {
      if (params['validation_id']) {
        this.validationConfigService.getValidationConfig(params['validation_id']).subscribe(
          valrun => {
            console.log('Val run:', valrun);
            //this.modelFromValidationConfig(valrun)
          }
        );
      } else {
        this.addDatasetToValidate();
        this.addReferenceDataset();
      }

    });
  }

  private modelFromValidationConfig(config: ValidationRunConfigDto) {
    config.dataset_configs.forEach(config => {
      let model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
      this.validationModel.datasetConfigurations.push(model);
      this.datasetService.getDatasetById(config.dataset_id).subscribe(dataset => {
        model.datasetModel.selectedDataset = dataset;
      });

      this.versionService.getVersionById(config.version_id).subscribe(versionDto => {
        model.datasetModel.selectedVersion = versionDto;
      });

      this.variableService.getVariableById(config.variable_id).subscribe(variableDto => {
        model.datasetModel.selectedVariable = variableDto;
      });


    });
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
        },
        () => {
        },
        () => this.setDefaultValidationPeriod()
      );

      // in the same time get the variables too
      this.variableService.getVariablesByDataset(model.datasetModel.selectedDataset.id).subscribe(variables => {
        model.datasetModel.selectedVariable = variables[0];
      });

      //and the filters
      this.updateDatasetConfigFilters(model);
    });
  }

  private updateDatasetConfigFilters(model: DatasetConfigModel) {
    this.filterService.getFiltersByDatasetId(model.datasetModel.selectedDataset.id).subscribe(filters => {
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
    this.setDefaultValidationPeriod();
  }

  onDatasetChange(datasetConfig: DatasetComponentSelectionModel) {
    this.validationModel.datasetConfigurations.forEach(config => {
      if (config.datasetModel == datasetConfig) {
        this.updateDatasetConfigFilters(config);
      }
    });
    this.setDefaultValidationPeriod();
  }

  onReferenceChange() {
    this.updateDatasetConfigFilters(this.validationModel.referenceConfigurations[0]);
    this.setDefaultValidationPeriod();
  }


  addDatasetButtonDisabled(): boolean {
    return this.validationModel.datasetConfigurations.length >= MAX_DATASETS_FOR_VALIDATION;
  }

  public startValidation() {
    //debug

    //prepare the dataset dtos (dataset, version, variable and filter settings)
    let datasets: ValidationRunDatasetConfigDto[] = [];
    this.validationModel.datasetConfigurations.forEach(datasetConfig => {
      datasets.push(datasetConfig.toValRunDatasetConfigDto());
    });

    //prepare metrics
    let metricDtos: ValidationRunMetricConfigDto[] = [];
    this.validationModel.metrics.forEach(metric => {
      metricDtos.push(metric.toValidationRunMetricDto());
    });

    let newValidation: ValidationRunConfigDto = {
      dataset_configs: datasets,
      reference_config: this.validationModel.referenceConfigurations[0].toValRunDatasetConfigDto(),
      interval_from: this.validationModel.validationPeriodModel.intervalFrom,
      interval_to: this.validationModel.validationPeriodModel.intervalTo,
      min_lat: this.validationModel.spatialSubsetModel.minLat$.getValue(),
      min_lon: this.validationModel.spatialSubsetModel.minLon$.getValue(),
      max_lat: this.validationModel.spatialSubsetModel.maxLat$.getValue(),
      max_lon: this.validationModel.spatialSubsetModel.maxLon$.getValue(),
      metrics: metricDtos,
      anomalies_method: this.validationModel.anomalies.method,
      anomalies_from: this.validationModel.anomalies.anomaliesFrom,
      anomalies_to: this.validationModel.anomalies.anomaliesTo,
      scaling_method: this.validationModel.scalingModel.id,
      scale_to: this.validationModel.scalingModel.scaleTo.id
    };

    this.validationConfigService.startValidation(newValidation).subscribe(
      data => {
        this.router.navigate([`validation-result/${data.id}`]).then(value => this.toastService.showSuccessWithHeader('Validation started', 'Your validation has been started'));
      },
      error => {
        this.toastService.showErrorWithHeader('Error', 'Your validation could not be started');
        console.error(error);
      });
  }

  setDefaultValidationPeriod(): void {
    const datesFrom = [];
    const datesTo = [];
    this.validationModel.datasetConfigurations.forEach(config => {
      if (config.datasetModel.selectedVersion.time_range_start && config.datasetModel.selectedVersion.time_range_end) {
        datesFrom.push(new Date(config.datasetModel.selectedVersion.time_range_start));
        datesTo.push(new Date(config.datasetModel.selectedVersion.time_range_end));
      }
    });

    this.validationModel.referenceConfigurations.forEach(config => {
      if (config.datasetModel.selectedVersion.time_range_start && config.datasetModel.selectedVersion.time_range_end) {
        datesFrom.push(new Date(config.datasetModel.selectedVersion.time_range_start));
        datesTo.push(new Date(config.datasetModel.selectedVersion.time_range_end));
      }
    });
    if (datesFrom.length !== 0) {
      this.validationStart = new Date(Math.max.apply(null, datesFrom));
    }
    if (datesTo.length !== 0) {
      this.validationEnd = new Date(Math.min.apply(null, datesTo));
    }

    this.validationModel.validationPeriodModel.intervalFrom = this.validationStart;
    this.validationModel.validationPeriodModel.intervalTo = this.validationEnd;
  }

}

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
import {
  ANOMALIES_NONE,
  ANOMALIES_NONE_DESC,
  AnomaliesComponent
} from '../../modules/anomalies/components/anomalies/anomalies.component';
import {SCALING_METHOD_DEFAULT, ScalingComponent} from '../../modules/scaling/components/scaling/scaling.component';
import {
  ValidationRunConfigDto,
  ValidationRunDatasetConfigDto,
  ValidationRunMetricConfigDto
} from './service/validation-run-config-dto';
import {ValidationRunConfigService} from './service/validation-run-config.service';

import {ToastService} from '../../modules/core/services/toast/toast.service';
import {ActivatedRoute, Router} from '@angular/router';
import {BehaviorSubject, ReplaySubject} from 'rxjs';
import {MapComponent} from '../../modules/map/components/map/map.component';
import {ValidationrunService} from '../../modules/core/services/validation-run/validationrun.service';
import {ModalWindowService} from '../../modules/core/services/global/modal-window.service';
import {ExistingValidationDto} from '../../modules/core/services/validation-run/existing-validation.dto';


const MAX_DATASETS_FOR_VALIDATION = 5;  //TODO: this should come from either config file or the database

@Component({
  selector: 'app-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
})
export class ValidateComponent implements OnInit, AfterViewInit {
  @ViewChild(MapComponent) child: MapComponent;
  @ViewChild(AnomaliesComponent) anomaliesChild: AnomaliesComponent;
  @ViewChild(ScalingComponent) scalingChild: ScalingComponent;

  mapVisible: BehaviorSubject<Boolean> = new BehaviorSubject<Boolean>(false);
  validationModel: ValidationModel = new ValidationModel(
    [],
    [],
    new SpatialSubsetModel(
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null)),
    new ValidationPeriodModel(new BehaviorSubject<Date>(null), new BehaviorSubject<Date>(null)),
    [],
    new AnomaliesModel(new BehaviorSubject<string>(ANOMALIES_NONE), ANOMALIES_NONE_DESC, new BehaviorSubject<Date>(null), new BehaviorSubject<Date>(null)),
    SCALING_METHOD_DEFAULT,
    new BehaviorSubject<string>(''));
  validationStart: Date = new Date('1978-01-01');
  validationEnd: Date = new Date();
  isThereValidation: ExistingValidationDto;
  public isExistingValidationWindowOpen: boolean;


  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService,
              private filterService: FilterService,
              private validationConfigService: ValidationRunConfigService,
              private validationRunService: ValidationrunService,
              private toastService: ToastService,
              private router: Router,
              private route: ActivatedRoute,
              private modalWindowService: ModalWindowService) {
  }

  ngAfterViewInit(): void {
    // child init could be done here
  }

  ngOnInit(): void {
    this.modalWindowService.watch().subscribe(state => {
      this.isExistingValidationWindowOpen = state === 'open';
    });

    this.route.queryParams.subscribe(params => {
      if (params['validation_id']) {
        this.validationConfigService.getValidationConfig(params['validation_id']).subscribe(
          valrun => {
            console.log('Val run:', valrun);
            this.modelFromValidationConfig(valrun);
          }
        );
      } else {
        this.addDatasetToValidate();
        this.addReferenceDataset();
      }

    });
  }

  private modelFromValidationConfig(config: ValidationRunConfigDto) {

    //Prepare dataset config
    config.dataset_configs.forEach(datasetConfig => {
      let model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
      this.validationModel.datasetConfigurations.push(model);
      this.datasetService.getDatasetById(datasetConfig.dataset_id).subscribe(dataset => {
        model.datasetModel.selectedDataset = dataset;
        this.loadFiltersForModel(model)//Load the available filters for the dataset
          .subscribe(model => { //when it is loaded, set the values from the config
            datasetConfig.basic_filters.forEach(basicFilterConfig => {
              model.basicFilters.forEach(filter => {
                if (basicFilterConfig == filter.filterDto.id) {
                  filter.enabled = true;
                }
              });
            });

          });
      });

      this.versionService.getVersionById(datasetConfig.version_id).subscribe(versionDto => {
        model.datasetModel.selectedVersion = versionDto;
      });

      this.variableService.getVariableById(datasetConfig.variable_id).subscribe(variableDto => {
        model.datasetModel.selectedVariable = variableDto;
      });
    });

    //Prepare reference
    let referenceModel = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
    this.validationModel.referenceConfigurations.push(referenceModel);
    this.datasetService.getDatasetById(config.reference_config.dataset_id).subscribe(dataset => {
      referenceModel.datasetModel.selectedDataset = dataset;
      this.loadFiltersForModel(referenceModel)
        .subscribe(model => { //when it is loaded, set the values from the config
          config.reference_config.basic_filters.forEach(basicFilterConfig => {
            model.basicFilters.forEach(filter => {
              if (basicFilterConfig == filter.filterDto.id) {
                filter.enabled = true;
              }
            });
          });
        });
    });

    this.versionService.getVersionById(config.reference_config.version_id).subscribe(versionDto => {
      referenceModel.datasetModel.selectedVersion = versionDto;
    });

    this.variableService.getVariableById(config.reference_config.variable_id).subscribe(variableDto => {
      referenceModel.datasetModel.selectedVariable = variableDto;
    });

    //Spatial subset
    this.validationModel.spatialSubsetModel.maxLon$.next(config.max_lon);
    this.validationModel.spatialSubsetModel.maxLat$.next(config.max_lat);
    this.validationModel.spatialSubsetModel.minLon$.next(config.min_lon);
    this.validationModel.spatialSubsetModel.minLat$.next(config.min_lat);

    //Temporal subset
    if (config.interval_from != null) {
      this.validationModel.validationPeriodModel.intervalFrom$.next(new Date(config.interval_from));
    }

    if (config.interval_to != null) {
      this.validationModel.validationPeriodModel.intervalTo$.next(new Date(config.interval_to));
    }

    //Metrics
    if (config.metrics) {
      config.metrics.forEach(metricDto => {
        this.validationModel.metrics.forEach(metricModel => {
          if (metricModel.id == metricDto.id) {
            metricModel.value$.next(metricDto.value);
          }
        });
      });
    }


    //Anomalies
    if (config.anomalies_method != null) {
      this.anomaliesChild.setSelection(config.anomalies_method);
      if (config.anomalies_from != null) {
        this.validationModel.anomalies.anomaliesFrom$.next(new Date(config.anomalies_from));
      }
      if (config.anomalies_to != null) {
        this.validationModel.anomalies.anomaliesTo$.next(new Date(config.anomalies_from));
      }
    }

    //Scaling
    this.scalingChild.setSelection(config.scaling_method, config.scale_to);

    // Name
    this.validationModel.nameTag$.next(config.name_tag);
  }

  addDatasetToValidate() {
    this.addDataset(this.validationModel.datasetConfigurations, 'C3S');
  }

  addReferenceDataset() {
    this.addDataset(this.validationModel.referenceConfigurations, 'ISMN');
  }

  private addDataset(targetArray: DatasetConfigModel[], defaultDatasetName: string) {
    let model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
    targetArray.push(model);
    //get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      model.datasetModel.selectedDataset = datasets.find(dataset => dataset.short_name === defaultDatasetName);

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
      this.loadFiltersForModel(model);
    });
  }

  private loadFiltersForModel(model: DatasetConfigModel): ReplaySubject<DatasetConfigModel> {
    let updatedModel$ = new ReplaySubject<DatasetConfigModel>();
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
        updatedModel$.next(model);
      },
      error => {
        updatedModel$.error(error);
      });
    return updatedModel$;
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
        this.loadFiltersForModel(config);
      }
    });
    this.setDefaultValidationPeriod();
  }

  onReferenceChange() {
    this.loadFiltersForModel(this.validationModel.referenceConfigurations[0]);
    this.setDefaultValidationPeriod();
  }


  addDatasetButtonDisabled(): boolean {
    return this.validationModel.datasetConfigurations.length >= MAX_DATASETS_FOR_VALIDATION;
  }

  public startValidation(checkForExistingValidation: boolean) {
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
      interval_from: this.validationModel.validationPeriodModel.intervalFrom$.getValue(),
      interval_to: this.validationModel.validationPeriodModel.intervalTo$.getValue(),
      min_lat: this.validationModel.spatialSubsetModel.minLat$.getValue(),
      min_lon: this.validationModel.spatialSubsetModel.minLon$.getValue(),
      max_lat: this.validationModel.spatialSubsetModel.maxLat$.getValue(),
      max_lon: this.validationModel.spatialSubsetModel.maxLon$.getValue(),
      metrics: metricDtos,
      anomalies_method: this.validationModel.anomalies.method$.getValue(),
      anomalies_from: this.validationModel.anomalies.anomaliesFrom$.getValue(),
      anomalies_to: this.validationModel.anomalies.anomaliesTo$.getValue(),
      scaling_method: this.validationModel.scalingModel.id,
      scale_to: this.validationModel.scalingModel.scaleTo$.getValue().id,
      name_tag: this.validationModel.nameTag$.getValue()
    };

    this.validationConfigService.startValidation(newValidation, checkForExistingValidation).subscribe(

      data => {
        if (data.id){
          this.router.navigate([`validation-result/${data.id}`]).then(value => this.toastService.showSuccessWithHeader('Validation started', 'Your validation has been started'));
        } else if (data.is_there_validation){
          this.isThereValidation = data;
          this.modalWindowService.open();
        }

      },
      error => {
        this.toastService.showErrorWithHeader('Error', 'Your validation could not be started');
        console.error(error);
      });
  }

  setDefaultValidationPeriod(): void {
    const datesFrom = [];
    const datesTo = [];

    if (this.validationModel.datasetConfigurations.length > 0){
      this.validationModel.datasetConfigurations.forEach(config => {
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_start) {
          datesFrom.push(new Date(config.datasetModel.selectedVersion.time_range_start));
        }
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_end) {
          datesTo.push(new Date(config.datasetModel.selectedVersion.time_range_end));
        }
      });
    }

    if (this.validationModel.referenceConfigurations.length > 0){
      this.validationModel.referenceConfigurations.forEach(config => {
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_start ) {
          datesFrom.push(new Date(config.datasetModel.selectedVersion.time_range_start));
        }
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_end) {
          datesTo.push(new Date(config.datasetModel.selectedVersion.time_range_end));
        }
      });
    }

    if (datesFrom.length !== 0) {
      this.validationStart = new Date(Math.max.apply(null, datesFrom));
    }
    if (datesTo.length !== 0) {
      this.validationEnd = new Date(Math.min.apply(null, datesTo));
    }

    this.validationModel.validationPeriodModel.intervalFrom$.next(this.validationStart);
    this.validationModel.validationPeriodModel.intervalTo$.next(this.validationEnd);
  }

}

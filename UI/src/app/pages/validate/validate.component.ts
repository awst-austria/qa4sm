import {AfterViewInit, Component, OnInit, ViewChild} from '@angular/core';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {
  DatasetComponentSelectionModel
} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../modules/core/services/dataset/dataset-variable.service';
import {DatasetConfigModel, ISMN_DEPTH_FILTER_ID, ISMN_NETWORK_FILTER_ID} from './dataset-config-model';
import {FilterService} from '../../modules/core/services/filter/filter.service';
import {FilterModel} from '../../modules/filter/components/basic-filter/filter-model';
import {ValidationModel} from './validation-model';
import {SpatialSubsetModel} from '../../modules/spatial-subset/components/spatial-subset/spatial-subset-model';
import {
  ValidationPeriodModel
} from '../../modules/validation-period/components/validation-period/validation-period-model';
import {AnomaliesModel} from '../../modules/anomalies/components/anomalies/anomalies-model';
import {
  ANOMALIES_NONE,
  ANOMALIES_NONE_DESC,
  AnomaliesComponent
} from '../../modules/anomalies/components/anomalies/anomalies.component';
import {SCALING_METHOD_DEFAULT, ScalingComponent} from '../../modules/scaling/components/scaling/scaling.component';
import {
  ConfigurationChanges,
  ValidationRunConfigDto,
  ValidationRunDatasetConfigDto,
  ValidationRunMetricConfigDto
} from './service/validation-run-config-dto';
import {ValidationRunConfigService} from './service/validation-run-config.service';

import {ToastService} from '../../modules/core/services/toast/toast.service';
import {ActivatedRoute, Router} from '@angular/router';
import {BehaviorSubject, of, ReplaySubject} from 'rxjs';
import {MapComponent} from '../../modules/map/components/map/map.component';
import {ModalWindowService} from '../../modules/core/services/global/modal-window.service';
import {ExistingValidationDto} from '../../modules/core/services/validation-run/existing-validation.dto';
import {delay} from 'rxjs/operators';
import {SettingsService} from '../../modules/core/services/global/settings.service';


const MAX_DATASETS_FOR_VALIDATION = 5;  // TODO: this should come from either config file or the database

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

  mapVisible: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  validationModel: ValidationModel = new ValidationModel(
    [],
    [],
    new SpatialSubsetModel(
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<boolean>(false),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null),
      new BehaviorSubject<number>(null)),
    new ValidationPeriodModel(new BehaviorSubject<Date>(null), new BehaviorSubject<Date>(null)),
    [],
    new AnomaliesModel(
      new BehaviorSubject<string>(ANOMALIES_NONE),
      ANOMALIES_NONE_DESC,
      new BehaviorSubject<Date>(null),
      new BehaviorSubject<Date>(null)),
    SCALING_METHOD_DEFAULT,
    new BehaviorSubject<string>(''));

  validationStart: Date = new Date('1978-01-01');
  validationEnd: Date = new Date();
  isThereValidation: ExistingValidationDto;
  public isExistingValidationWindowOpen: boolean;
  maintenanceMode = false;

  defMaxLon = 48.3;
  defMinLon = -11.2;
  defMaxLat = 71.6;
  defMinLat = 34.0;

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService,
              private filterService: FilterService,
              private validationConfigService: ValidationRunConfigService,
              private toastService: ToastService,
              private router: Router,
              private route: ActivatedRoute,
              private modalWindowService: ModalWindowService,
              private settingsService: SettingsService) {
  }

  ngAfterViewInit(): void {
    // child init could be done here
  }

  ngOnInit(): void {
    this.settingsService.getAllSettings().subscribe(setting => {
      this.maintenanceMode = setting[0].maintenance_mode;
    });
    this.modalWindowService.watch().subscribe(state => {
      this.isExistingValidationWindowOpen = state === 'open';
    });

    this.route.queryParams.subscribe(params => {
      if (params.validation_id) {
        this.validationConfigService.getValidationConfig(params.validation_id).subscribe(
          valrun => {
            this.modelFromValidationConfig(valrun);
            if (valrun.changes){
              this.toastService.showAlertWithHeader('Not all settings could be reloaded.',
                this.messageAboutConfigurationChanges(valrun.changes));
            }
          },
          (response) => {
            if (response.message){
              this.toastService.showErrorWithHeader('Reloading impossible', response.error.message);
            }
            of({}).pipe(delay(0)).subscribe(() => {
              this.setDefaultGeographicalRange();
            });
            this.addDatasetToValidate();
            this.addReferenceDataset();
          }
        );
      } else {
        of({}).pipe(delay(0)).subscribe(() => {
          this.setDefaultGeographicalRange();
        });
        this.addDatasetToValidate();
        this.addReferenceDataset();
      }

    });
  }

  private messageAboutConfigurationChanges(changes: ConfigurationChanges): string{
    let message = '';
    if (changes.scaling) {
      message += 'Chosen scaling method is not available anymore. "No scaling" set instead.\n';
    }
    if (changes.anomalies) {
      message += '\nChosen anomalies method is not available anymore. "Do not calculate" set instead.\n';
    }
    if (changes.filters.length !== 0){
      changes.filters.forEach(filter => {
        message += `\nFilters:${filter.filter_desc.map(desc => ' ' + desc)} for dataset ${filter.dataset} not available.`;
      });
    }

    return message.toString();
  }

  private modelFromValidationConfig(validationRunConfig: ValidationRunConfigDto): void {
    // TODO: parameterized filter setup seems to be missing
    // Prepare dataset config
    validationRunConfig.dataset_configs.forEach(datasetConfig => {
      const newDatasetConfigModel = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null),
        null, new BehaviorSubject(null), new BehaviorSubject(null));
      this.validationModel.datasetConfigurations.push(newDatasetConfigModel);
      this.datasetService.getDatasetById(datasetConfig.dataset_id).subscribe(dataset => {
        newDatasetConfigModel.datasetModel.selectedDataset = dataset;
        this.loadFiltersForModel(newDatasetConfigModel, true) // Load the available filters for the dataset, set default parameters
          .subscribe(datasetConfigModel => { // when it is loaded, set the parameter values from the config
            datasetConfig.basic_filters.forEach(basicFilterConfig => {
              datasetConfigModel.basicFilters.forEach(filter => {
                if (basicFilterConfig === filter.filterDto.id) {
                  filter.enabled = true;
                }
              });
            });
            datasetConfig.parametrised_filters.forEach(paramFilter => {
              if (paramFilter.id === ISMN_NETWORK_FILTER_ID) {
                datasetConfigModel.ismnNetworkFilter$.value.parameters$.next(paramFilter.parameters);

              }
              if (paramFilter.id === ISMN_DEPTH_FILTER_ID) {
                datasetConfigModel.ismnDepthFilter$.value.parameters$.next(paramFilter.parameters);
              }
            });
          });
      });

      this.versionService.getVersionById(datasetConfig.version_id).subscribe(versionDto => {
        newDatasetConfigModel.datasetModel.selectedVersion = versionDto;
      });

      this.variableService.getVariableById(datasetConfig.variable_id).subscribe(variableDto => {
        newDatasetConfigModel.datasetModel.selectedVariable = variableDto;
      });
    });

    // Prepare reference
    const newReferenceModel = new DatasetConfigModel(
      new DatasetComponentSelectionModel(null, null, null), null,
      new BehaviorSubject<FilterModel>(null), new BehaviorSubject<FilterModel>(null));
    this.validationModel.referenceConfigurations.push(newReferenceModel);
    this.datasetService.getDatasetById(validationRunConfig.reference_config.dataset_id).subscribe(dataset => {
      newReferenceModel.datasetModel.selectedDataset = dataset;
      this.loadFiltersForModel(newReferenceModel, true)
        .subscribe(referenceConfigModel => { // when it is loaded, set the values from the config
          validationRunConfig.reference_config.basic_filters.forEach(basicFilterConfig => {
            referenceConfigModel.basicFilters.forEach(filter => {
              if (basicFilterConfig === filter.filterDto.id) {
                filter.enabled = true;
              }
            });
          });
          validationRunConfig.reference_config.parametrised_filters.forEach(paramFilter => {
            if (paramFilter.id === ISMN_NETWORK_FILTER_ID) {
              referenceConfigModel.ismnNetworkFilter$.value.parameters$.next(paramFilter.parameters);
            }
            if (paramFilter.id === ISMN_DEPTH_FILTER_ID) {
              referenceConfigModel.ismnDepthFilter$.value.parameters$.next(paramFilter.parameters);
            }
          });
        });
    });

    this.versionService.getVersionById(validationRunConfig.reference_config.version_id).subscribe(versionDto => {
      newReferenceModel.datasetModel.selectedVersion = versionDto;
    });

    this.variableService.getVariableById(validationRunConfig.reference_config.variable_id).subscribe(variableDto => {
      newReferenceModel.datasetModel.selectedVariable = variableDto;
    });

    // Spatial subset
    this.validationModel.spatialSubsetModel.maxLon$.next(validationRunConfig.max_lon);
    this.validationModel.spatialSubsetModel.maxLat$.next(validationRunConfig.max_lat);
    this.validationModel.spatialSubsetModel.minLon$.next(validationRunConfig.min_lon);
    this.validationModel.spatialSubsetModel.minLat$.next(validationRunConfig.min_lat);

    // Temporal subset
    if (validationRunConfig.interval_from != null) {
      this.validationModel.validationPeriodModel.intervalFrom$.next(new Date(validationRunConfig.interval_from));
    }

    if (validationRunConfig.interval_to != null) {
      this.validationModel.validationPeriodModel.intervalTo$.next(new Date(validationRunConfig.interval_to));
    }

    // Metrics
    if (validationRunConfig.metrics) {
      validationRunConfig.metrics.forEach(metricDto => {
        this.validationModel.metrics.forEach(metricModel => {
          if (metricModel.id === metricDto.id) {
            metricModel.value$.next(metricDto.value);
          }
        });
      });
    }


    // Anomalies
    if (validationRunConfig.anomalies_method != null) {
      this.anomaliesChild.setSelection(validationRunConfig.anomalies_method);
      if (validationRunConfig.anomalies_from != null) {
        this.validationModel.anomalies.anomaliesFrom$.next(new Date(validationRunConfig.anomalies_from));
      }
      if (validationRunConfig.anomalies_to != null) {
        this.validationModel.anomalies.anomaliesTo$.next(new Date(validationRunConfig.anomalies_from));
      }
    }

    // Scaling
    this.scalingChild.setSelection(validationRunConfig.scaling_method, validationRunConfig.scale_to);

    // Name
    this.validationModel.nameTag$.next(validationRunConfig.name_tag);
  }

  includeFilter(toInclude: string, basicFilters: any, enabled: boolean): void {
    // Simultaneously include/exclude all filters that are mutually inclusive (e.g. flag==0 and flag!=1, flag!=2)
    const toIncludeIds = [];
    toInclude.split(',').forEach(
      id => toIncludeIds.push(Number(id))
    );
    basicFilters.forEach(filter => {
      if (toIncludeIds.includes(filter.filterDto.id)) {
        filter.enabled = enabled;
        filter.readonly = enabled;
      }
    });
  }

  isIncluded(id: number, basicFilters: any): boolean {
    let itDoes = false;
    basicFilters.forEach(filter => {
      const toIncludeIds = [];
      const toInclude = filter.filterDto.to_include;
      if (toInclude !== null) {
        toInclude.split(',').forEach(
          filterId => toIncludeIds.push(Number(filterId))
        );
      }
      if (toIncludeIds.includes(id)) {
        itDoes = true;
      }
    });
    return itDoes;
  }

  addDatasetToValidate(): void {
    this.addDataset(this.validationModel.datasetConfigurations, 'C3S_combined', 'v202012');
  }

  addReferenceDataset(): void {
    this.addDataset(this.validationModel.referenceConfigurations, 'ISMN', '20210131 global');
  }

  private addDataset(targetArray: DatasetConfigModel[], defaultDatasetName: string, defaultVersionName: string): void {
    const model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null),
      null, new BehaviorSubject(null), new BehaviorSubject(null));
    targetArray.push(model);
    // get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      model.datasetModel.selectedDataset = datasets.find(dataset => dataset.short_name === defaultDatasetName);

      // then get all versions for the first dataset in the result list
      this.versionService.getVersionsByDataset(model.datasetModel.selectedDataset.id).subscribe(versions => {
          model.datasetModel.selectedVersion = versions.find((version => version.pretty_name === defaultVersionName));
        },
        () => {
        },
        () => {
          this.setDefaultValidationPeriod();
          this.setLimitationsOnGeographicalRange();
        }
      );

      // at the same time get the variables too
      this.variableService.getVariablesByDataset(model.datasetModel.selectedDataset.id).subscribe(variables => {
        model.datasetModel.selectedVariable = variables[0];
      });

      // and the filters
      this.loadFiltersForModel(model);
    });
  }


  private loadFiltersForModel(model: DatasetConfigModel, reloadingSettings = false): ReplaySubject<DatasetConfigModel> {
    const updatedModel$ = new ReplaySubject<DatasetConfigModel>();
    this.filterService.getFiltersByDatasetId(model.datasetModel.selectedDataset.id).subscribe(filters => {
        model.basicFilters = [];
        model.ismnNetworkFilter$.next(null);
        model.ismnDepthFilter$.next(null);
        filters.forEach(filter => {
          if (filter.parameterised) {
            if (filter.id === ISMN_NETWORK_FILTER_ID) {
              model.ismnNetworkFilter$.next(new FilterModel(
                filter,
                false,
                false,
                new BehaviorSubject<string>(filter.default_parameter)));
            } else if (filter.id === ISMN_DEPTH_FILTER_ID) {
              if (model.ismnDepthFilter$) {
                model.ismnDepthFilter$.next(new FilterModel(
                  filter,
                  false,
                  false,
                  new BehaviorSubject<string>(filter.default_parameter)));
              } else {
                model.ismnDepthFilter$ = new BehaviorSubject<FilterModel>(new FilterModel(
                  filter,
                  false,
                  false,
                  new BehaviorSubject<string>(filter.default_parameter))
                );
              }
            }
          } else {
            const newFilter = (new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(null)));
            if (!reloadingSettings && newFilter.filterDto.default_set_active) {
              newFilter.enabled = true;
            }
            model.basicFilters.push(newFilter);
          }
        });

        updatedModel$.next(model);
      },
      error => {
        updatedModel$.error(error);
      });

    return updatedModel$;
  }

  removeDataset(configModel: DatasetConfigModel): void {
    const toBeRemoved = this.validationModel.datasetConfigurations.indexOf(configModel);
    if (toBeRemoved > -1) {
      this.validationModel.datasetConfigurations.splice(toBeRemoved, 1);
    }
    this.setDefaultValidationPeriod();
    this.setLimitationsOnGeographicalRange();
  }

  onDatasetChange(datasetConfig: DatasetComponentSelectionModel): void {
    this.validationModel.datasetConfigurations.forEach(config => {
      if (config.datasetModel === datasetConfig) {
        this.loadFiltersForModel(config);
      }
    });
    this.setDefaultValidationPeriod();
    this.setLimitationsOnGeographicalRange();
  }

  onReferenceChange(): void {
    this.loadFiltersForModel(this.validationModel.referenceConfigurations[0]);
    this.setDefaultValidationPeriod();
    this.setLimitationsOnGeographicalRange();
  }

  excludeFilter(toExclude: number, basicFilters: any): void {
    // Exclude the filter if mutual is selected
    basicFilters.forEach(filter => {
      if (filter.filterDto.id === toExclude) {
        filter.enabled = false;
      }
    });
  }

  addDatasetButtonDisabled(): boolean {
    return this.validationModel.datasetConfigurations.length >= MAX_DATASETS_FOR_VALIDATION;
  }

  public startValidation(checkForExistingValidation: boolean): void {
    // prepare the dataset dtos (dataset, version, variable and filter settings)
    const datasets: ValidationRunDatasetConfigDto[] = [];
    this.validationModel.datasetConfigurations.forEach(datasetConfig => {
      datasets.push(datasetConfig.toValRunDatasetConfigDto());
    });

    // prepare metrics
    const metricDtos: ValidationRunMetricConfigDto[] = [];
    this.validationModel.metrics.forEach(metric => {
      metricDtos.push(metric.toValidationRunMetricDto());
    });

    const newValidation: ValidationRunConfigDto = {
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
        if (data.id) {
          this.router.navigate([`validation-result/${data.id}`]).then(value => this.toastService.showSuccessWithHeader('Validation started', 'Your validation has been started'));
        } else if (data.is_there_validation) {
          this.isThereValidation = data;
          this.modalWindowService.open();
        }

      },
      error => {
        this.toastService.showErrorWithHeader('Error', 'Your validation could not be started');
      });
  }

  setDefaultGeographicalRange(): void {
    this.validationModel.spatialSubsetModel.maxLon$.next(this.defMaxLon);
    this.validationModel.spatialSubsetModel.minLon$.next(this.defMinLon);
    this.validationModel.spatialSubsetModel.maxLat$.next(this.defMaxLat);
    this.validationModel.spatialSubsetModel.minLat$.next(this.defMinLat);
  }

  setLimitationsOnGeographicalRange(): void {
    const maxLons = [];
    const minLons = [];
    const maxLats = [];
    const minLats = [];

    // check if there are geographical limits in both reference and non-reference datasets
    if (this.validationModel.datasetConfigurations.length > 0) {
      this.validationModel.datasetConfigurations.forEach(config => {
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.geographical_range) {
          maxLons.push(config.datasetModel.selectedVersion.geographical_range.max_lon);
          minLons.push(config.datasetModel.selectedVersion.geographical_range.min_lon);
          maxLats.push(config.datasetModel.selectedVersion.geographical_range.max_lat);
          minLats.push(config.datasetModel.selectedVersion.geographical_range.min_lat);
        }
      });
    }

    if (this.validationModel.referenceConfigurations.length > 0) {
      this.validationModel.referenceConfigurations.forEach(config => {
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.geographical_range) {
          maxLons.push(config.datasetModel.selectedVersion.geographical_range.max_lon);
          minLons.push(config.datasetModel.selectedVersion.geographical_range.min_lon);
          maxLats.push(config.datasetModel.selectedVersion.geographical_range.max_lat);
          minLats.push(config.datasetModel.selectedVersion.geographical_range.min_lat);
        }
      });
    }

    // get current values of the spatial subsetting
    const lonMaxCurrent = this.validationModel.spatialSubsetModel.maxLon$.value;
    const lonMinCurrent = this.validationModel.spatialSubsetModel.minLon$.value;
    const latMaxCurrent = this.validationModel.spatialSubsetModel.maxLat$.value;
    const latMinCurrent = this.validationModel.spatialSubsetModel.minLat$.value;
    // new limits
    const lonMaxLimit = Math.min(...maxLons);
    const lonMinLimit = Math.max(...minLons);
    const latMaxLimit = Math.min(...maxLats);
    const latMinLimit = Math.max(...minLats);

    // conditions to verify
    const isGeographicallyLimited = minLats.length !== 0 || minLons.length !== 0 || maxLats.length !== 0 || minLats.length !== 0;
    const hasTheSameOrSmallerRange = lonMaxLimit >= lonMaxCurrent && lonMinLimit <= lonMinCurrent &&
      latMaxLimit >= latMaxCurrent && latMinLimit <= latMinCurrent;

    // push the condition and the new value if conditions are met
    this.validationModel.spatialSubsetModel.limited$.next(isGeographicallyLimited);

    // push the condition and the new value if conditions are met
    if (maxLons.length !== 0 && lonMaxLimit < lonMaxCurrent || (maxLons.length !== 0 && lonMaxCurrent === this.defMaxLon)) {
      this.validationModel.spatialSubsetModel.maxLon$.next(lonMaxLimit);
      this.validationModel.spatialSubsetModel.maxLonLimit$.next(lonMaxLimit);
    }

    if (minLons.length !== 0 && lonMinLimit > lonMinCurrent || (minLons.length !== 0 && lonMinCurrent === this.defMinLon)) {
      this.validationModel.spatialSubsetModel.minLon$.next(lonMinLimit);
      this.validationModel.spatialSubsetModel.minLonLimit$.next(lonMinLimit);
    }

    if (maxLats.length !== 0 && latMaxLimit < latMaxCurrent || (maxLats.length !== 0 && latMaxCurrent === this.defMaxLat)) {
      this.validationModel.spatialSubsetModel.maxLat$.next(latMaxLimit);
      this.validationModel.spatialSubsetModel.maxLatLimit$.next(latMaxLimit);
    } else if (maxLats.length !== 0){
      this.validationModel.spatialSubsetModel.maxLatLimit$.next(latMaxLimit);
    }

    if (minLats.length !== 0 && latMinLimit > latMinCurrent || (minLats.length !== 0 && latMinCurrent === this.defMinLat)) {
      this.validationModel.spatialSubsetModel.minLat$.next(latMinLimit);
      this.validationModel.spatialSubsetModel.minLatLimit$.next(latMinLimit);
    }

    // inform a user about the automatic change
    if (isGeographicallyLimited && !hasTheSameOrSmallerRange) {
      this.toastService.showAlert('The chosen spatial subsetting is bigger than the one covered by chosen datasets. ' +
        'Bounds corrected to fit available subsetting');
    }

  }

  setDefaultValidationPeriod(): void {
    const datesFrom = [];
    const datesTo = [];

    if (this.validationModel.datasetConfigurations.length > 0) {
      this.validationModel.datasetConfigurations.forEach(config => {
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_start) {
          datesFrom.push(new Date(config.datasetModel.selectedVersion.time_range_start));
        }
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_end) {
          datesTo.push(new Date(config.datasetModel.selectedVersion.time_range_end));
        }
      });
    }

    if (this.validationModel.referenceConfigurations.length > 0) {
      this.validationModel.referenceConfigurations.forEach(config => {
        if (config.datasetModel.selectedVersion && config.datasetModel.selectedVersion.time_range_start) {
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

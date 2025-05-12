import { AfterViewInit, Component, OnInit, signal, ViewChild } from '@angular/core';
import { DatasetService } from '../../modules/core/services/dataset/dataset.service';
import {
  DatasetComponentSelectionModel
} from '../../modules/dataset/components/dataset/dataset-component-selection-model';
import { DatasetVersionService } from '../../modules/core/services/dataset/dataset-version.service';
import { DatasetVariableService } from '../../modules/core/services/dataset/dataset-variable.service';
import {
  DatasetConfigModel,
  ISMN_DEPTH_FILTER_ID,
  ISMN_NETWORK_FILTER_ID,
  SMAP_L3_STATIC_WATER_FILTER_ID,
  SMAP_L3_V9_VWC_FILTER_ID,
  SMOS_CHI2_FILTER_ID,
  SMOS_RFI_FILTER_ID
} from './dataset-config-model';
import { FilterService } from '../../modules/core/services/filter/filter.service';
import { FilterModel } from '../../modules/filter/components/basic-filter/filter-model';
import { ValidationModel } from './validation-model';
import { SpatialSubsetModel } from '../../modules/spatial-subset/components/spatial-subset/spatial-subset-model';
import {
  ValidationPeriodModel
} from '../../modules/validation-period/components/validation-period/validation-period-model';
import { AnomaliesModel } from '../../modules/anomalies/components/anomalies/anomalies-model';
import {
  ANOMALIES_NONE,
  ANOMALIES_NONE_DESC,
  AnomaliesComponent
} from '../../modules/anomalies/components/anomalies/anomalies.component';
import { ScalingComponent } from '../../modules/scaling/components/scaling/scaling.component';
import {
  ConfigurationChanges,
  ValidationRunConfigDto,
  ValidationRunDatasetConfigDto,
  ValidationRunMetricConfigDto
} from './service/validation-run-config-dto';
import { ValidationRunConfigService } from './service/validation-run-config.service';

import { ToastService } from '../../modules/core/services/toast/toast.service';
import { ActivatedRoute, Router } from '@angular/router';
import { BehaviorSubject, EMPTY, forkJoin, Observable, of, ReplaySubject } from 'rxjs';
import { MapComponent } from '../../modules/map/components/map/map.component';
import { ModalWindowService } from '../../modules/core/services/global/modal-window.service';
import { ExistingValidationDto } from '../../modules/core/services/validation-run/existing-validation.dto';
import { catchError, delay, map } from 'rxjs/operators';
import { SettingsService } from '../../modules/core/services/global/settings.service';
import {
  TemporalMatchingModel
} from '../../modules/temporal-matching/components/temporal-matching/temporal-matching-model';
import { ReferenceModel } from '../../modules/validation-reference/components/validation-reference/reference-model';
import { ScalingModel } from '../../modules/scaling/components/scaling/scaling-model';
import {
  ValidationReferenceComponent
} from '../../modules/validation-reference/components/validation-reference/validation-reference.component';
import { AuthService } from '../../modules/core/services/auth/auth.service';
import { CustomHttpError } from '../../modules/core/services/global/http-error.service';


const MAX_DATASETS_FOR_VALIDATION = 6;  // TODO: this should come from either config file or the database

//NOTE the maximum number of datasets is already defined in the backend, maybe it could be used here?
// from validator.validation.globals import MAX_NUM_DS_PER_VAL_RUN;
// const MAX_DATASETS_FOR_VALIDATION = MAX_NUM_DS_PER_VAL_RUN;

@Component({
  selector: 'qa-validate',
  templateUrl: './validate.component.html',
  styleUrls: ['./validate.component.scss'],
})
export class ValidateComponent implements OnInit, AfterViewInit {
  @ViewChild(MapComponent) mapComponent: MapComponent;
  @ViewChild(AnomaliesComponent) anomaliesChild: AnomaliesComponent;
  @ViewChild(ScalingComponent) scalingChild: ScalingComponent;
  @ViewChild('spatialReference') spatialReferenceChild: ValidationReferenceComponent;
  @ViewChild('temporalReference') temporalReferenceChild: ValidationReferenceComponent;

  validationModel: ValidationModel;

  validationStart: Date = new Date('1978-01-01');
  validationEnd: Date = new Date();
  isThereValidation: ExistingValidationDto;
  public isExistingValidationWindowOpen: boolean;
  maintenanceMode = false;
  noIsmnPoints = signal(false);
  noVariable = signal(false);
  noVersion = signal(false);
  noFilters = signal(false);
  validationDisabledMessage = new BehaviorSubject(''); // can not be signal, because it is used in html

  defMaxLon = 48.3;
  defMinLon = -11.2;
  defMaxLat = 71.6;
  defMinLat = 34.0;

  highlightedDataset: DatasetConfigModel;

  getValidationConfigObserver = {
    next: valrun => this.onGetValidationConfigNext(valrun),
    error: error => this.onGetValidationConfigError(error),
  }

  startValidationObserver = {
    next: data => this.onStartValidationNext(data),
    error: error => this.onStartValidationError(error)
  }

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private variableService: DatasetVariableService,
              private filterService: FilterService,
              public validationConfigService: ValidationRunConfigService,
              private toastService: ToastService,
              private router: Router,
              private route: ActivatedRoute,
              private modalWindowService: ModalWindowService,
              private settingsService: SettingsService,
              public authService: AuthService) {
  }

  ngAfterViewInit(): void {
    this.updateMap();
  }


  ngOnInit(): void {
    this.resetValidationModel();
    this.settingsService.getAllSettings().subscribe(setting => {
      this.maintenanceMode = setting[0].maintenance_mode;
    });
    this.modalWindowService.watch().subscribe(state => {
      this.isExistingValidationWindowOpen = state === 'open';
    });

    this.route.queryParams.subscribe(params => {
      if (params.validation_id) {
        this.validationConfigService.getValidationConfig(params.validation_id).subscribe(
          this.getValidationConfigObserver
        );
      } else {
        this.setDefaultDatasetSettings();
      }
    });
    this.validationConfigService.listOfSelectedConfigs.next(this.validationModel.datasetConfigurations);
  }

  resetValidationModel(): void {
    this.validationModel = new ValidationModel(
      [],
      new ReferenceModel(null, null, null),
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
      {intra_annual_metrics: false, intra_annual_type: "", intra_annual_overlap: null},
      new AnomaliesModel(
        new BehaviorSubject<string>(ANOMALIES_NONE),
        ANOMALIES_NONE_DESC,
        signal<number>(null),
        signal<number>(null)),
      new TemporalMatchingModel(
        new BehaviorSubject<number>(null),
        'hours',
      ),
      new ScalingModel('', ''),
      new BehaviorSubject<string>(''));
  }

  private onGetValidationConfigNext(valrun: ValidationRunConfigDto): void {
    this.modelFromValidationConfig(valrun);

    setTimeout(() => {
      if (valrun.changes) {
        alert(`Not all settings could be reloaded. \n ${this.messageAboutConfigurationChanges(valrun.settings_changes)}`)
      }
    }, 300);
  }

  private onGetValidationConfigError(response): void {
    if (response.message) {
      this.toastService.showErrorWithHeader('Reloading impossible', response.error.message);
    }
    this.setDefaultDatasetSettings();
  }

  private setDefaultDatasetSettings(): void {
    this.resetValidationModel();
    of({}).pipe(delay(0)).subscribe(() => {
      this.setDefaultGeographicalRange();
    });
    this.addDatasetToValidate('ISMN',
      undefined, true, true, false, true);
    this.addDatasetToValidate(undefined,
      undefined, undefined, undefined, true);
  }

  private messageAboutConfigurationChanges(changes: ConfigurationChanges): string {
    let message = '';
    if (changes.scaling) {
      message += 'Chosen scaling method is not available anymore. "No scaling" set instead.\n';
    }
    if (changes.anomalies) {
      message += '\nChosen anomalies method is not available anymore. "Do not calculate" set instead.\n';
    }
    if (changes.filters.length !== 0) {
      changes.filters.forEach(filter => {
        message += `\nFilters: ${filter.filter_desc.map(desc => desc)} for dataset ${filter.dataset} not available.`;
      });
    }
    if (changes.versions.length !== 0) {
      changes.versions.forEach(version => {
        message += `\nVersion: ${version.version} of ${version.dataset} is no longer available. The newest available versions set instead.\n`;
      })
    }
    return message.toString();
  }

  private modelFromValidationConfig(validationRunConfig: ValidationRunConfigDto): void {
    // Prepare dataset config
    validationRunConfig.dataset_configs.forEach(datasetConfig => {
      const newDatasetConfigModel = new DatasetConfigModel(
        new DatasetComponentSelectionModel(null, null, null),
        null,
        new BehaviorSubject(null),
        new BehaviorSubject(null),
        new BehaviorSubject(null),
        new BehaviorSubject(null),
        new BehaviorSubject(false),
        new BehaviorSubject(false),
        new BehaviorSubject(false),
        new BehaviorSubject(null),
        new BehaviorSubject(null),
        new BehaviorSubject(false)
      );
      this.validationModel.datasetConfigurations.push(newDatasetConfigModel);
      this.versionService.getVersionById(datasetConfig.version_id).subscribe({
        next: versionDto => {
          newDatasetConfigModel.datasetModel.selectedVersion = versionDto;

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
                if (paramFilter.id === SMOS_RFI_FILTER_ID) {
                  datasetConfigModel.smosRfiFilter$.value.parameters$.next(paramFilter.parameters);
                }
                if (paramFilter.id === SMOS_CHI2_FILTER_ID) {
                  datasetConfigModel.smosChi2Filter$.value.parameters$.next(paramFilter.parameters);
                }
                if (paramFilter.id === ISMN_NETWORK_FILTER_ID) {
                  datasetConfigModel.ismnNetworkFilter$.value.parameters$.next(paramFilter.parameters);
                }
                if (paramFilter.id === ISMN_DEPTH_FILTER_ID) {
                  datasetConfigModel.ismnDepthFilter$.value.parameters$.next(paramFilter.parameters);
                }
                if (paramFilter.id == SMAP_L3_V9_VWC_FILTER_ID){
                  datasetConfigModel.vegetationWaterFilter$.value.parameters$.next(paramFilter.parameters);
                }
                if (paramFilter.id == SMAP_L3_STATIC_WATER_FILTER_ID){
                  datasetConfigModel.staticWaterFilter$.value.parameters$.next(paramFilter.parameters);
                }

              });
            });
        },
        error: (error: CustomHttpError) => this.onGetVersionError(error)

      });

      this.variableService.getVariableById(datasetConfig.variable_id)
        .subscribe({
          next: variableDto => newDatasetConfigModel.datasetModel.selectedVariable = variableDto,
          error: (error: CustomHttpError) => this.onGetVariableError(error)
        });

      newDatasetConfigModel.spatialReference$.next(datasetConfig.is_spatial_reference);
      newDatasetConfigModel.temporalReference$.next(datasetConfig.is_temporal_reference);
      newDatasetConfigModel.scalingReference$.next(datasetConfig.is_scaling_reference);

      this.datasetService.getDatasetById(datasetConfig.dataset_id)
        .pipe(
          catchError(() => EMPTY)
        )
        .subscribe(dataset => {
          newDatasetConfigModel.datasetModel.selectedDataset = dataset;

          if (datasetConfig.is_spatial_reference) {
            this.spatialReferenceChild.setReference(newDatasetConfigModel);
          }
          if (datasetConfig.is_temporal_reference) {
            this.temporalReferenceChild.setReference(newDatasetConfigModel);
          }
          if (datasetConfig.is_scaling_reference) {
            this.scalingChild.setSelection(validationRunConfig.scaling_method, newDatasetConfigModel);
          }

        });
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
    // Temporal matching window size
    this.validationModel.temporalMatchingModel.size$.next(validationRunConfig.temporal_matching);

    // Metrics
    if (validationRunConfig.metrics) {
      validationRunConfig.metrics.forEach(metricDto => {
        this.validationModel.metrics.forEach(metricModel => {
          if (metricModel.name === metricDto.id) {
            metricModel.value = metricDto.value;
          }
        });
      });
    }

    // Intra-Annual Metrics
    this.validationModel.intraAnnualMetrics = validationRunConfig.intra_annual_metrics;

    // Anomalies
    if (validationRunConfig.anomalies_method != null) {
      this.anomaliesChild.setSelection(validationRunConfig.anomalies_method);
      if (validationRunConfig.anomalies_from != null) {
        this.validationModel.anomalies.anomaliesFrom.set((new Date(validationRunConfig.anomalies_from)).getFullYear());
      }
      if (validationRunConfig.anomalies_to != null) {
        this.validationModel.anomalies.anomaliesTo.set((new Date(validationRunConfig.anomalies_to)).getFullYear());
      }
    }


    // Scaling
    // this.scalingChild.setSelection(validationRunConfig.scaling_method, scaleTo);
    // this.spatialReferenceChild.setReference(spatialReference);
    // this.temporalReferenceChild.setReference(temporalReference);

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

  addDatasetToValidate(defaultDatasetName = 'C3S_combined', defaultVersionName = undefined, userData = true,
                       spatialReference = false, temporalReference = false, scalingReference = false): void {
    this.addDataset(this.validationModel.datasetConfigurations, defaultDatasetName, defaultVersionName, userData,
      spatialReference, temporalReference);
  }

  private addDataset(targetArray: DatasetConfigModel[], defaultDatasetName: string, defaultVersionName: string,
                     userData: boolean, spatialReference: boolean, temporalReference: boolean): void {
    const model = new DatasetConfigModel(
      new DatasetComponentSelectionModel(null, null, null),
      null,
      new BehaviorSubject(null),
      new BehaviorSubject(null),
      new BehaviorSubject(null),
      new BehaviorSubject(null),
      new BehaviorSubject(spatialReference),
      new BehaviorSubject(temporalReference),
      new BehaviorSubject(false),
      new BehaviorSubject(null),
      new BehaviorSubject(null),
      new BehaviorSubject(false)
    );
    targetArray.push(model);
    // get all datasets
    this.datasetService.getAllDatasets(userData)
      .pipe(
        catchError(() => EMPTY)
      )
      .subscribe(datasets => {
        model.datasetModel.selectedDataset = datasets.find(dataset => dataset.short_name === defaultDatasetName);


        const getVersionsByDatasetObserver = {
          next: versions => this.onGetVersionNext(versions, model, defaultVersionName),
          error: (error: CustomHttpError) => this.onGetVersionError(error),
          complete: () => this.onGetVersionComplete(),
        }


        // then get all versions for the first dataset in the result list
        this.versionService.getVersionsByDataset(model.datasetModel.selectedDataset.id).subscribe(
          getVersionsByDatasetObserver
        );

        // at the same time get the variables too
        // this.variableService.getVariablesByVersion(model.datasetModel.selectedVersion.id)
        //   .subscribe(getVariablesByDatasetObserver);

        // and the filters
        // this.loadFiltersForModel(model);
      });
  }

  private onGetVariableError(error: CustomHttpError): void {
    this.noVariable.set(true);
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
  }


  private onGetVersionNext(versions, model, defaultVersionName): void {
    const getVariablesByDatasetObserver = {
      next: variables => model.datasetModel.selectedVariable = variables[0],
      error: (error: CustomHttpError) => this.onGetVariableError(error),
    }


    model.datasetModel.selectedVersion = defaultVersionName ? versions.find((version => version.pretty_name === defaultVersionName)) : versions[0];
    this.loadFiltersForModel(model)
    this.variableService.getVariablesByVersion(model.datasetModel.selectedVersion.id)
      .subscribe(getVariablesByDatasetObserver);
  }

  private onGetVersionError(error: CustomHttpError): void {
    this.noVersion.set(true);
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
  }

  private onGetVersionComplete(): void {
    this.setDefaultValidationPeriod();
    this.setLimitationsOnGeographicalRange();
  }


  private loadFiltersForModel(model: DatasetConfigModel, reloadingSettings = false): ReplaySubject<DatasetConfigModel> {
    const updatedModel$ = new ReplaySubject<DatasetConfigModel>();

    const getFiltersObserver = {
      next: filters => this.onGetFiltersNext(filters, model, reloadingSettings, updatedModel$),
      error: error => this.onGetFiltersError(error, updatedModel$)
    }
    this.filterService.getFiltersByVersionId(model.datasetModel.selectedVersion.id).subscribe(getFiltersObserver);
    return updatedModel$;
  }


  private onGetFiltersNext(filters, model, reloadingSettings, updatedModel$): void {
    model.basicFilters = [];
    model.smosRfiFilter$.next(null);
    model.ismnNetworkFilter$.next(null);
    model.ismnDepthFilter$.next(null);
    model.smosChi2Filter$.next(null);
    model.vegetationWaterFilter$.next(null);
    model.staticWaterFilter$.next(null);
    filters.forEach(filter => {
      if (filter.parameterised) {
        if (filter.id === ISMN_NETWORK_FILTER_ID) {
          model.ismnNetworkFilter$.next(new FilterModel(
            filter,
            false,
            false,
            new BehaviorSubject<string>(filter.default_parameter)));
        } else if (filter.id === SMOS_RFI_FILTER_ID) {
          if (model.smosRfiFilter$) {
            model.smosRfiFilter$.next(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter)));
          } else {
            model.smosRfiFilter$ = new BehaviorSubject<FilterModel>(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter))
            );
          }
        } else if (filter.id === SMAP_L3_STATIC_WATER_FILTER_ID) {
          if (model.staticWaterFilter$) {
            model.staticWaterFilter$.next(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter)));
          } else {
            model.staticWaterFilter$ = new BehaviorSubject<FilterModel>(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter))
            );
          }
        } else if (filter.id === SMAP_L3_V9_VWC_FILTER_ID) {
          if (model.vegetationWaterFilter$) {
            model.vegetationWaterFilter$.next(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter)));
          } else {
            model.vegetationWaterFilter$ = new BehaviorSubject<FilterModel>(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter))
            );
          }
        } else if (filter.id === SMOS_CHI2_FILTER_ID) {
          if (model.smosChi2Filter$) {
            model.smosChi2Filter$.next(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter)));
          } else {
            model.smosChi2Filter$ = new BehaviorSubject<FilterModel>(new FilterModel(
              filter,
              false,
              false,
              new BehaviorSubject<string>(filter.default_parameter))
            );
          }
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
  }

  private onGetFiltersError(error, updatedModel$): void {
    this.noFilters.set(true);
    updatedModel$.error(error);
  }

  removeDataset(configModel: DatasetConfigModel): void {
    const toBeRemoved = this.validationModel.datasetConfigurations.indexOf(configModel);
    if (toBeRemoved > -1) {
      this.validationModel.datasetConfigurations.splice(toBeRemoved, 1);
    }
    this.setDefaultValidationPeriod();
    this.setLimitationsOnGeographicalRange();

    this.checkIfReferenceRemoved('spatialReference$');
    this.checkIfReferenceRemoved('temporalReference$');
    this.checkIfReferenceRemoved('scalingReference$');

    this.validationConfigService.listOfSelectedConfigs.next(this.validationModel.datasetConfigurations);
    this.updateMap();
  }

  checkIfReferenceRemoved(referenceType: string): void {
    if (!this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig[referenceType].getValue())) {
      let newReference = this.validationModel.datasetConfigurations[0];
      if (referenceType === 'spatialReference$') {
        const ISMNList = this.getISMN(this.validationModel.datasetConfigurations);
        if (ISMNList.length !== 0) {
          newReference = ISMNList[0];
        }
      }
      if (referenceType === 'temporalReference$') {
        const nonISMNList = this.validationModel.datasetConfigurations
          .filter(config => config.datasetModel.selectedDataset.short_name !== 'ISMN');
        newReference = nonISMNList[0];
      }
      if (referenceType === 'scalingReference$' && this.validationModel.scalingMethod.methodName === 'none') {
        newReference[referenceType].next(false);
      } else {
        newReference[referenceType].next(true);
      }
    }
  }

  onDatasetChange(datasetConfig: DatasetComponentSelectionModel): void {
    const isThereISMN = this.getISMN(this.validationModel.datasetConfigurations).length !== 0;
    this.validationModel.datasetConfigurations.forEach(config => {
      if (config.datasetModel === datasetConfig) {
        this.loadFiltersForModel(config);
        if (datasetConfig.selectedDataset.pretty_name === 'ISMN' && config.temporalReference$.getValue()) {
          config.temporalReference$.next(false);
        }
      }
      if (isThereISMN) {
        config.datasetModel.selectedDataset.pretty_name === 'ISMN' ? config.spatialReference$.next(true) :
          config.spatialReference$.next(false);
      }
    });
    this.checkIfReferenceRemoved('temporalReference$');
    this.setDefaultValidationPeriod();
    this.setLimitationsOnGeographicalRange();
    this.validationConfigService.listOfSelectedConfigs.next(this.validationModel.datasetConfigurations);


    //map update
    this.updateMap();
  }

  onIsmnNetworkSelectionChange(selectedNetworks: string): void {
    this.updateMap();
  }

  onIsmnDepthSelectionChange(selectedNetworks: string): void {
    this.updateMap();
  }

  onBasicFilterMapUpdate($event): void {
    if ($event) {
      this.updateMap()
    }
  }

  updateMap() {
    let geojsons: Observable<any>[] = [];
    this.validationModel.datasetConfigurations.forEach(config => {
      if (config.datasetModel.selectedVersion) {
        geojsons.push(this.versionService.getGeoJSONById(config.datasetModel.selectedVersion.id).pipe(map(value => {
            let filteredGeoJson: any = JSON.parse(value);

            if (config.ismnDepthFilter$.value != null) {
              filteredGeoJson = this.ismnDepthFilter(config.ismnDepthFilter$.value.parameters$.value, filteredGeoJson);
            }
            if (config.ismnNetworkFilter$.value != null) {
              filteredGeoJson = this.ismnNetworkFilter(config.ismnNetworkFilter$.value.parameters$.value, filteredGeoJson);
            }


            config.basicFilters.forEach(filter => {
              if (filter.filterDto.name === 'FIL_ISMN_FRM_representative' && filter.enabled) {
                filteredGeoJson = this.ismnFrmFilter(filteredGeoJson)
              }
            })

            return filteredGeoJson;
          }),
          catchError(error => of(undefined))
        ));
      }
    });

    forkJoin(geojsons).subscribe(data => {
      this.mapComponent.clearSelection();
      data.forEach(mapData => {
        if (mapData != undefined) {
          this.mapComponent.addGeoJson(JSON.stringify(mapData));
        }
      });
    });

  }

  private ismnDepthFilter(filter: string, geoJson: any): any {
    const numbers: string[] = filter.split(',');
    const geoJsonObj = geoJson;
    if (numbers.length === 2) {
      const minVal: number = parseFloat(numbers[0]);
      const maxVal: number = parseFloat(numbers[1]);
      if (!isNaN(minVal) && !isNaN(maxVal)) {

        const filteredFeatures: any[] = geoJsonObj.features.filter((feature: any) => {
          const minDepthValue = parseFloat(
            feature.properties.datasetProperties.find((prop: any) => prop.propertyName === "depth_from")?.propertyValue || "0"
          );
          const maxDepthValue = parseFloat(
            feature.properties.datasetProperties.find((prop: any) => prop.propertyName === "depth_to")?.propertyValue || "0"
          );
          // If min_depth or max_depth property is missing or not a valid number, include the feature in the result
          if (isNaN(minDepthValue) || isNaN(maxDepthValue)) {
            return true;
          }
          return minDepthValue >= minVal && maxDepthValue <= maxVal;
        });

        return {
          type: geoJsonObj.type,
          features: filteredFeatures,
        };
      } else {
        console.error("Invalid ISMN depth filter param. value:", filter);
      }
    } else {
      console.error("Invalid ISMN depth filter param. value:", filter);
    }

  }

  private ismnNetworkFilter(filter: string, geoJsonObj: any): any {
    const filteredFeatures: any[] = geoJsonObj.features.filter((feature: any) => {
      const actualNetwork = feature.properties.datasetProperties.find((prop: any) => prop.propertyName === "network")?.propertyValue || "Unknown"
      return filter.includes(actualNetwork);
    });

    return {
      type: geoJsonObj.type,
      features: filteredFeatures,
    };
  }

  private ismnFrmFilter(geoJsonObj: any): any {
    const representativeClasses = ['representative', 'very representative'];
    const filteredFeatures: any[] = geoJsonObj.features.filter((feature: any) =>
      representativeClasses.includes(feature.properties.datasetProperties.find((prop: any) => prop.propertyName === "frm_class")?.propertyValue)
    )
    return {
      type: geoJsonObj.type,
      features: filteredFeatures,
    };
  }


  private getISMN(configs: DatasetConfigModel[]): DatasetConfigModel[] {
    return configs.filter(config => config.datasetModel.selectedDataset.short_name === 'ISMN');
  }


  addDatasetButtonDisabled(): boolean {
    return this.validationModel.datasetConfigurations.length >= MAX_DATASETS_FOR_VALIDATION;
  }

  public startValidation(checkForExistingValidation: boolean): void {

    if (!this.authService.authenticated.value) {
      this.toastService.showErrorWithHeader('Cannot start validation', 'You must be logged in to start a validation.');
      this.authService.switchLoginModal(true, 'Please log in to start validation');
      return;
    }

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

    this.validationModel.referenceConfigurations.spatial =
      this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig.spatialReference$);
    this.validationModel.referenceConfigurations.temporal =
      this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig.temporalReference$);
    this.validationModel.referenceConfigurations.scaling =
      this.validationModel.datasetConfigurations.find(datasetConfig => datasetConfig.scalingReference$);

    const newValidation: ValidationRunConfigDto = {
      dataset_configs: datasets,
      interval_from: this.validationModel.validationPeriodModel.intervalFrom$.getValue(),
      interval_to: this.validationModel.validationPeriodModel.intervalTo$.getValue(),
      min_lat: this.validationModel.spatialSubsetModel.minLat$.getValue(),
      min_lon: this.validationModel.spatialSubsetModel.minLon$.getValue(),
      max_lat: this.validationModel.spatialSubsetModel.maxLat$.getValue(),
      max_lon: this.validationModel.spatialSubsetModel.maxLon$.getValue(),
      metrics: metricDtos,
      intra_annual_metrics: this.validationModel.intraAnnualMetrics,
      anomalies_method: this.validationModel.anomalies.method$.getValue(),
      anomalies_from: new Date(this.validationModel.anomalies.anomaliesFrom(), 0, 1),
      anomalies_to: new Date(this.validationModel.anomalies.anomaliesTo(), 11, 31),
      scaling_method: this.validationModel.scalingMethod.methodName,
      scale_to: '0',
      name_tag: this.validationModel.nameTag$.getValue(),
      temporal_matching: this.validationModel.temporalMatchingModel.size$.getValue()
    };
    this.validationConfigService.startValidation(newValidation, checkForExistingValidation)
      .subscribe(this.startValidationObserver);
  }

  private onStartValidationNext(data): void {
    if (data.id) {
      this.router.navigate([`validation-result/${data.id}`]).then(() =>
        this.toastService.showSuccessWithHeader('Validation started',
          'Your validation has been started'));
    } else if (data.is_there_validation) {
      this.isThereValidation = data;
      this.modalWindowService.open();
    }
  }

  private onStartValidationError(error) {
    if (this.authService.authenticated.getValue()) {
      const validationErrorMessage = this.messageAboutValidationErrors(error);
      this.toastService.showErrorWithHeader('Error', 'Your validation could not be started. \n\n' + validationErrorMessage);
    }
  }

  setDefaultGeographicalRange(): void {
    this.validationModel.spatialSubsetModel.maxLon$.next(this.defMaxLon);
    this.validationModel.spatialSubsetModel.minLon$.next(this.defMinLon);
    this.validationModel.spatialSubsetModel.maxLat$.next(this.defMaxLat);
    this.validationModel.spatialSubsetModel.minLat$.next(this.defMinLat);
  }

  getCurrentSpatialSubseting(): { lonMax: number, lonMin: number, latMax: number, latMin: number } {
    return {
      lonMax: this.validationModel.spatialSubsetModel.maxLon$.value,
      lonMin: this.validationModel.spatialSubsetModel.minLon$.value,
      latMax: this.validationModel.spatialSubsetModel.maxLat$.value,
      latMin: this.validationModel.spatialSubsetModel.minLat$.value
    };
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

    // get current values of the spatial subsetting;
    let currentVals = this.getCurrentSpatialSubseting();
    // new limits
    const lonMaxLimit = Math.min(...maxLons);
    const lonMinLimit = Math.max(...minLons);
    const latMaxLimit = Math.min(...maxLats);
    const latMinLimit = Math.max(...minLats);

    // conditions to verify
    const isGeographicallyLimited = minLats.length !== 0 || minLons.length !== 0 || maxLats.length !== 0 || minLats.length !== 0;
    const hasTheSameOrSmallerRange = lonMaxLimit >= currentVals.lonMax && lonMinLimit <= currentVals.lonMin &&
      latMaxLimit >= currentVals.latMax && latMinLimit <= currentVals.latMin;

    // push the condition and the new value if conditions are met
    this.validationModel.spatialSubsetModel.limited$.next(isGeographicallyLimited);

    // push the condition and the new value if conditions are met
    if (maxLons.length !== 0 && lonMaxLimit < currentVals.lonMax ||
      (maxLons.length !== 0 && currentVals.lonMax === this.defMaxLon)) {
      this.validationModel.spatialSubsetModel.maxLon$.next(lonMaxLimit);
      this.validationModel.spatialSubsetModel.maxLonLimit$.next(lonMaxLimit);
    } else if (maxLons.length !== 0) {
      this.validationModel.spatialSubsetModel.maxLonLimit$.next(lonMaxLimit);
    }

    if (minLons.length !== 0 && lonMinLimit > currentVals.lonMin ||
      (minLons.length !== 0 && currentVals.lonMin === this.defMinLon)) {
      this.validationModel.spatialSubsetModel.minLon$.next(lonMinLimit);
      this.validationModel.spatialSubsetModel.minLonLimit$.next(lonMinLimit);
    } else if (minLons.length !== 0) {
      this.validationModel.spatialSubsetModel.minLonLimit$.next(lonMinLimit);
    }

    if (maxLats.length !== 0 && latMaxLimit < currentVals.latMax ||
      (maxLats.length !== 0 && currentVals.latMax === this.defMaxLat)) {
      this.validationModel.spatialSubsetModel.maxLat$.next(latMaxLimit);
      this.validationModel.spatialSubsetModel.maxLatLimit$.next(latMaxLimit);
    } else if (maxLats.length !== 0) {
      this.validationModel.spatialSubsetModel.maxLatLimit$.next(latMaxLimit);
    }

    if (minLats.length !== 0 && latMinLimit > currentVals.latMin ||
      (minLats.length !== 0 && currentVals.latMin === this.defMinLat)) {
      this.validationModel.spatialSubsetModel.minLat$.next(latMinLimit);
      this.validationModel.spatialSubsetModel.minLatLimit$.next(latMinLimit);
    } else if (minLats.length !== 0) {
      this.validationModel.spatialSubsetModel.minLatLimit$.next(latMinLimit);
    }


    // I need to repeat it, because there might be a case where min and max are the same, but bigger/smaller than the
    // limit, and in such a case both needs to be updated
// again get current values of the spatial subsetting
    currentVals = this.getCurrentSpatialSubseting();

    if (currentVals.latMin > currentVals.latMax && latMinLimit) {
      this.validationModel.spatialSubsetModel.minLat$.next(latMinLimit);
      this.validationModel.spatialSubsetModel.minLatLimit$.next(latMinLimit);
    } else if (currentVals.latMin > currentVals.latMax && !latMinLimit) {
      this.validationModel.spatialSubsetModel.maxLat$.next(currentVals.latMax);
    }

    if (currentVals.latMax < latMinLimit && latMaxLimit) {
      this.validationModel.spatialSubsetModel.maxLat$.next(latMaxLimit);
      this.validationModel.spatialSubsetModel.maxLatLimit$.next(latMaxLimit);
    } else if (currentVals.latMax < latMinLimit && !latMaxLimit) {
      this.validationModel.spatialSubsetModel.maxLat$.next(latMinLimit);
    }

    if (currentVals.lonMin > currentVals.lonMax && lonMinLimit) {
      this.validationModel.spatialSubsetModel.minLon$.next(lonMinLimit);
      this.validationModel.spatialSubsetModel.minLonLimit$.next(lonMinLimit);
    } else if (currentVals.lonMin > currentVals.lonMax && !lonMinLimit) {
      this.validationModel.spatialSubsetModel.minLon$.next(currentVals.lonMax);
    }

    if (currentVals.lonMax < currentVals.lonMin && lonMaxLimit) {
      this.validationModel.spatialSubsetModel.maxLon$.next(lonMaxLimit);
      this.validationModel.spatialSubsetModel.maxLonLimit$.next(lonMaxLimit);
    } else if (currentVals.lonMax < currentVals.lonMin && !lonMaxLimit) {
      this.validationModel.spatialSubsetModel.maxLon$.next(currentVals.lonMin);
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

    if (datesFrom.length !== 0) {
      this.validationStart = new Date(Math.max.apply(null, datesFrom));
    }
    if (datesTo.length !== 0) {
      this.validationEnd = new Date(Math.min.apply(null, datesTo));
    }

    this.validationModel.validationPeriodModel.intervalFrom$.next(this.validationStart);
    this.validationModel.validationPeriodModel.intervalTo$.next(this.validationEnd);
  }

  private getValidationFieldFriendlyName(fieldName): string {
    const fieldsFriendlyNames = {
      name_tag: 'validation name',
      interval_from: 'validation period "From"',
      interval_to: 'validation period "To"',
      anomalies: 'anomalies',
      min_lat: 'minimum latitude',
      max_lat: 'maximum latitude',
      min_lon: 'minimum longitude',
      max_lon: 'maximum longitude',
    };
    return fieldsFriendlyNames[fieldName];
  }

  private messageAboutValidationErrors(errors: any): string {
    let message = 'Please fix following problems: \n';

    Object.entries(errors.error).forEach(([key]) => {
      if (this.getValidationFieldFriendlyName(key)) {
        message += `\n Field ${this.getValidationFieldFriendlyName(key)}: ${errors.error[key]} \n`;
      } else {
        message += `\n ${errors.error[key]}`;
      }
    });

    return message.toString();
  }

  onHoverOverReferenceDataset(event): void {
    this.highlightedDataset = event.hoveredDataset;
    this.highlightedDataset.highlighted$.next(event.highlight);
  }

  disableValidateButton(validationModel): boolean {
    const noneVariable = validationModel.datasetConfigurations
      .filter(config => config.datasetModel?.selectedVariable?.short_name === '--none--').length !== 0;
    let message = 'You can not start a validation, ';
    if (noneVariable) {
      message += 'because one of the chosen dataset has no variable assigned.'
    } else if (this.noIsmnPoints()) {
      message += 'because there are not ISMN points available for comparison.'
    } else if (this.noVersion()) {
      message += 'because no version is available.'
    } else if (this.noVariable()) {
      message += 'because no variable is available.'
    } else if (this.noFilters()) {
      message += 'because we could not fetch filters properly.'
    }
    this.validationDisabledMessage.next(message);
    return noneVariable || this.noIsmnPoints() || this.noVariable() || this.noVersion() || this.noFilters()
  }

  public checkIsmnPoints(evt): void {
    this.noIsmnPoints.set(evt)
  }

}

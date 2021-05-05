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
import {NewValidationRunDto} from './service/new-validation-run-dto';
import {NewValRunDatasetConfigDto} from './service/new-val-run-dataset-config-dto';
import {NewValidationRunService} from './service/new-validation-run.service';
import {NewValidationRunMetricDto} from './service/new-validation-run-metric-dto';
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
  validationrunId: string;
  mapCenter = [100, 100];

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
              private newValidationService: NewValidationRunService,
              private toastService: ToastService,
              private router: Router,
              private route: ActivatedRoute,
              private validationrunService: ValidationrunService) {

  }

  ngAfterViewInit(): void {
    // child init could be done here
  }

  ngOnInit(): void {
    // console.log('Monika', this.route.snapshot.paramMap.get('validationId'));
    this.validationrunId = this.route.snapshot.paramMap.get('validationId');
    // console.log(this.validationrunId);
    if (this.validationrunId){
      this.readValidationSettings(this.validationrunId, this.validationModel);
    }
    // console.log('validation run in ngOnInit', this.validationModel);
    // this.addDatasetToValidate();
    // this.addReferenceDataset();
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
    let datasets: NewValRunDatasetConfigDto[] = [];
    this.validationModel.datasetConfigurations.forEach(datasetConfig => {
      datasets.push(datasetConfig.toNewValRunDatasetConfigDto());
    });

    //prepare metrics
    let metricDtos: NewValidationRunMetricDto[] = [];
    this.validationModel.metrics.forEach(metric => {
      metricDtos.push(metric.toNewValidationRunMetricDto());
    });

    let newValidationDto = new NewValidationRunDto(
      datasets,
      this.validationModel.referenceConfigurations[0].toNewValRunDatasetConfigDto(),
      this.validationModel.spatialSubsetModel.toNewValSpatialSubsettingDto(),
      this.validationModel.validationPeriodModel.toNewValidationRunValidationPeriodDto(),
      metricDtos,
      this.validationModel.anomalies.toNewValidationRunAnomaliesDto(),
      this.validationModel.scalingModel.toNewValidationRunScalingDto());

    this.newValidationService.startValidation(newValidationDto).subscribe(
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


  readValidationSettings(validationId: string, validationModel: ValidationModel): void {
    // console.log('taken from resolver: ', this.route.snapshot.data.loadingSettings);
    this.validationrunService.getValidationRunById(validationId).subscribe(val => {
      // validationModel.spatialSubsetModel.setValues(val.max_lat, val.max_lon, val.min_lat, val.min_lon);
    });
    const validation = this.route.snapshot.data.loadingSettings;
    validationModel.anomalies.setAnomalies(this.route.snapshot.data.loadingSettings.anomalies,
      new Date(this.route.snapshot.data.loadingSettings.anomalies_from),
      new Date(this.route.snapshot.data.loadingSettings.anomalies_to));
    // console.log(this.validationModel);
    // let validationrun: ValidationrunDto;
    // this.route.data.subscribe(validation => {
    // this.validationrunService.getValidationRunById(validationId).subscribe(validation => {
    //     // validationModel.anomalies.method = validation.anomalies;
    //     // validationModel.anomalies.anomaliesFrom = new Date(validation.anomalies_from);
    //     // validationModel.anomalies.anomaliesTo = new Date(validation.anomalies_to);
    //     // validationModel.anomalies.setAnomalies(validation.anomalies, new Date(validation.anomalies_from),
    //     //   new Date(validation.anomalies_to));
    //     // console.log(validation.anomalies, new Date(validation.anomalies_from));
    //     // validationModel.anomalies.selected = true;
    //     // validationModel.anomalies.method = validation.anomalies;
    //     validationModel.anomalies.setAnomalies(validation.anomalies, ANOMALIES[validation.anomalies],
    //       new Date(validation.anomalies_from), new Date(validation.anomalies_to));
    //     // const anomaliesModel = new AnomaliesModel(validation.anomalies, ANOMALIES[validation.anomalies], validation.anomalies_from,
    //     //   validation.anomalies_to, true);
    //     // console.log('tralalala', anomaliesModel);
    //     // validationModel.anomalies = anomaliesModel;
    //
    validationModel.validationPeriodModel.intervalFrom = new Date(validation.interval_from);
    validationModel.validationPeriodModel.intervalTo = new Date(validation.interval_to);
    this.mapCenter = [(validation.max_lat + validation.min_lat) / 2, (validation.max_lon + validation.min_lon) / 2];
    const maxLat = new BehaviorSubject<number>(validation.max_lat);
    const maxLon = new BehaviorSubject<number>(validation.max_lon);
    const minLat = new BehaviorSubject<number>(validation.min_lat);
    const minLon = new BehaviorSubject<number>(validation.min_lon);
    // validationModel.spatialSubsetModel = new SpatialSubsetModel(maxLat, maxLon, minLat, minLon);
    validationModel.spatialSubsetModel.setValues(validation.max_lat, validation.max_lon, validation.min_lat, validation.min_lon);
    //
    //     // validationModel.metrics
    //   },
    //   () => {
    //   },
    //   () => {
    //
    //   });
  }
}

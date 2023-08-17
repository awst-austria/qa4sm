import {Component, EventEmitter, Input, OnDestroy, OnInit, Output} from '@angular/core';
import {ValidationResultModel} from '../../../../pages/validation-result/validation-result-model';
import {BehaviorSubject, combineLatest, Observable} from 'rxjs';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {FilterService} from '../../../core/services/filter/filter.service';
import {map} from 'rxjs/operators';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {Router} from '@angular/router';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationRunConfigService} from '../../../../pages/validate/service/validation-run-config.service';


@Component({
  selector: 'qa-validation-summary',
  templateUrl: './validation-summary.component.html',
  styleUrls: ['./validation-summary.component.scss']
})
export class ValidationSummaryComponent implements OnInit, OnDestroy {

  @Input() validationModel: ValidationResultModel;
  @Input() validationRun: ValidationrunDto;
  @Input() forComparison = false;
  @Output() doRefresh = new EventEmitter();

  configurations$: Observable<any>;
  dateFormat = 'medium';
  timeZone = 'UTC';
  hideElement = true;
  originalDate: Date;
  runTime: number;
  errorRate: number;
  isOwner: boolean;
  // some BS added to avoid refreshing component every time sth changes
  valName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  isArchived$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(null);
  expiryDate$: BehaviorSubject<Date> = new BehaviorSubject<Date>(null);
  isNearExpiry$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(null);

  faIcons = {faArchive: fas.faArchive, faPencil: fas.faPen};
  scalingMethod: string;
  public isPublishingWindowOpen: boolean;
  publishingInProgressInterval: any;
  publishingInProgress$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

  constructor(private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private filterService: FilterService,
              public globalParamsService: GlobalParamsService,
              private validationService: ValidationrunService,
              private authService: AuthService,
              private router: Router,
              public validationConfigService: ValidationRunConfigService) {
  }

  ngOnInit(): void {
    this.setInitialValues();
    this.updateConfig();
    this.getOriginalDate();
    this.validationConfigService.getScalingMethods().subscribe(methods => {
      this.scalingMethod = methods.find(method => method.method === this.validationRun.scaling_method).description;
    });
    this.checkIfPublishingInProgress();
  }

  getCurrentUser(): number {
    return this.authService.currentUser.id;
  }

  private updateConfig(): void {
    this.configurations$ = combineLatest(
      this.validationModel.datasetConfigs,
      this.datasetService.getAllDatasets(true, false),
      this.datasetVersionService.getAllVersions(),
      this.datasetVariableService.getAllVariables(),
      this.filterService.getAllFilters(),
      this.filterService.getAllParameterisedFilters()
    ).pipe(
      map(([configurations,
             datasets,
             versions,
             variables,
             dataFilters,
             paramFilters]) =>
        configurations.map(
          config => {
            const datasetInfo = datasets.find(ds => config.dataset === ds.id);

            return {
              ...config,
              dataset: datasetInfo?.pretty_name,

              fileExists: datasetInfo?.storage_path.length > 0,

              version: versions.find(dsVersion =>
                config.version === dsVersion.id).pretty_name,

              variable: variables.find(dsVar =>
                config.variable === dsVar.id).short_name,

              variableUnit: variables.find(dsVar =>
                config.variable === dsVar.id).unit,

              filters: config.filters.map(f => dataFilters.find(dsF => dsF.id === f).description),

              parametrisedFilters: config.parametrised_filters.map(f => dataFilters.find(dsF => dsF.id === f).description),

              parametrisedFiltersValues: config.parametrised_filters
                .map(fId => config.parametrisedfilter_set
                  .map(pf => [paramFilters.find(pF => pF.id === pf).filter_id, paramFilters
                    .find(pF => pF.id === pf).parameters])
                  .find(f => f[0] === fId)[1])

            }
          }
        ))
    );
  }

  getRunTime(startTime: Date, endTime: Date): number {
    const startTimeDate = new Date(startTime);
    const endTimeDate = new Date(endTime);
    const runTime = endTimeDate.getTime() - startTimeDate.getTime();
    return Math.round(runTime / 60000);
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  toggleEditing(): void {
    this.hideElement = !this.hideElement;
  }

  saveName(validationId: string, newName: string): void {
    this.validationService.saveResultsName(validationId, newName).subscribe(
      (resp) => {
        if (resp === 'Changed.'){
          this.valName$.next(newName);
          this.toggleEditing();
        }
      });
  }

  update(doUpdate: any): void {
    if (doUpdate.key === 'archived') {
      this.isArchived$.next(doUpdate.value === 'None');
      doUpdate.value !== 'None' ? this.expiryDate$.next(doUpdate.value) : this.expiryDate$.next(null);
    } else if (doUpdate.key === 'extended'){
      this.expiryDate$.next(doUpdate.value);
      this.isNearExpiry$.next(false);
    }
    else if (doUpdate.key === 'delete'){
      this.router.navigate(['/my-validations']);
    }
  }

  getOriginalDate(): void {
    this.validationModel.validationRun.subscribe(data => {
      if (data.is_a_copy) {
        this.validationService.getCopiedRunRecord(data.id).subscribe(copiedRun => {
          if (copiedRun.original_run_date) {
            this.originalDate = copiedRun.original_run_date;
          } else {
            this.originalDate = data.start_time;
          }
        });
      }
    });
  }

  setInitialValues(): void{
    this.runTime = this.getRunTime(this.validationRun.start_time, this.validationRun.end_time);
    this.errorRate = this.validationRun.total_points !== 0 ?
      (this.validationRun.total_points - this.validationRun.ok_points) / this.validationRun.total_points : 1;
    this.isOwner = this.validationRun.user === this.authService.currentUser.id;
    this.valName$.next(this.validationRun.name_tag);
    this.isArchived$.next(this.validationRun.is_archived);
    this.expiryDate$.next(this.validationRun.expiry_date);
    this.isNearExpiry$.next(this.validationRun.is_near_expiry);
  }

  checkIfPublishingInProgress(): void{
    if (this.validationRun.publishing_in_progress || this.publishingInProgress$.getValue()){
      this.publishingInProgressInterval = setInterval(() => {
        this.validationService.getValidationRunById(this.validationRun.id).subscribe(data => {
          if (!data.publishing_in_progress) {
            this.doRefresh.emit(true)
          }
        });
      }, 20 * 1000)

    }
  }

  handlePublishWindow(open): void{
    this.isPublishingWindowOpen = open;
  }

  startPublishing(): void{
    this.publishingInProgress$.next(true)
    this.checkIfPublishingInProgress()
  }

  ngOnDestroy(): void {
    clearInterval(this.publishingInProgressInterval);
  }

}

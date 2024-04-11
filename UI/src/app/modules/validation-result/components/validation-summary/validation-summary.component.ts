import {Component, EventEmitter, Input, OnDestroy, OnInit, Output, signal} from '@angular/core';
import {ValidationResultModel} from '../../../../pages/validation-result/validation-result-model';
import {combineLatest, EMPTY, Observable, of} from 'rxjs';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {FilterService} from '../../../core/services/filter/filter.service';
import {catchError, map} from 'rxjs/operators';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {Router} from '@angular/router';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ValidationRunConfigService} from '../../../../pages/validate/service/validation-run-config.service';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {ToastService} from '../../../core/services/toast/toast.service';


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
  originalDate = signal<Date | undefined>(undefined)
  runTime: number;
  errorRate: number;
  isOwner: boolean;
  dataFetchError = signal(false);
  // some BS added to avoid refreshing component every time sth changes
  valName = signal<string | undefined>(undefined);
  isArchived = signal<boolean | undefined>(undefined);
  expiryDate = signal<Date | undefined>(undefined);
  isNearExpiry = signal<boolean | undefined>(undefined);

  faIcons = {faArchive: fas.faArchive, faPencil: fas.faPen};
  public isPublishingWindowOpen: boolean;
  publishingInProgressInterval: any;
  publishingInProgress = signal<boolean>(false);
  scalingMethodDescription$ = this.validationConfigService.scalingMethods$.pipe(
    map(methods => methods
      .find(method => method.method === this.validationRun.scaling_method).description
    ),
    catchError(() => of('no information'))
  );

  constructor(private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private filterService: FilterService,
              public globalParamsService: GlobalParamsService,
              private validationService: ValidationrunService,
              private authService: AuthService,
              private router: Router,
              public validationConfigService: ValidationRunConfigService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.setInitialValues();
    this.updateConfig();
    this.getOriginalDate();
    this.checkIfPublishingInProgress();
  }

  getCurrentUser(): number {
    return this.authService.currentUser.id;
  }

  private updateConfig(): void {
    this.configurations$ = combineLatest(
      [this.validationModel.datasetConfigs$,
        this.datasetService.getAllDatasets(true, false),
        this.datasetVersionService.getAllVersions().pipe(
          catchError(() => of([]))
        ),
        this.datasetVariableService.getAllVariables().pipe(
          catchError(() => of([]))
        ),
        this.filterService.getAllFilters(),
        this.filterService.getAllParameterisedFilters()]
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

              version: versions.length ? versions.find(dsVersion =>
                config.version === dsVersion.id).pretty_name : '...',

              variable: variables.length ? variables.find(dsVar =>
                config.variable === dsVar.id).short_name : '...',

              variableUnit: variables.length ? variables.find(dsVar =>
                config.variable === dsVar.id).unit : '...',

              filters: config.filters.map(f => dataFilters.find(dsF => dsF.id === f).description),

              parametrisedFilters: config.parametrised_filters.map(f => dataFilters.find(dsF => dsF.id === f).description),

              parametrisedFiltersValues: config.parametrised_filters
                .map(fId => config.parametrisedfilter_set
                  .map(pf => [paramFilters.find(pF => pF.id === pf).filter_id, paramFilters
                    .find(pF => pF.id === pf).parameters])
                  .find(f => f[0] === fId)[1])

            }
          }
        )),
      catchError(() => {
        this.dataFetchError.set(true);
        return EMPTY
      })
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

  saveNameObserver = (newName: string) => {
    return {
      next: () => this.onNameSave(newName),
      error: (error: CustomHttpError) => this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
      complete: () => this.toastService.showSuccess('Name updated')
    }
  }

  onNameSave(newName: string): void {
    this.valName.set(newName);
    this.toggleEditing();
  }

  saveName(validationId: string, newName: string): void {
    this.validationService.saveResultsName(validationId, newName).subscribe(this.saveNameObserver(newName));
  }

  update(doUpdate: any): void {
    if (doUpdate.key === 'archived') {
      this.isArchived.set(doUpdate.value === 'None');
      doUpdate.value !== 'None' ? this.expiryDate.set(doUpdate.value) : this.expiryDate.set(null);
    } else if (doUpdate.key === 'extended') {
      this.expiryDate.set(doUpdate.value);
      this.isNearExpiry.set(false);
    } else if (doUpdate.key === 'delete') {
      this.router.navigate(['/my-validations']);
    }
  }

  getOriginalDate(): void {
    this.validationModel.validationRun$
      .subscribe(data => {
      if (data.is_a_copy) {
        this.validationService.getCopiedRunRecord(data.id)
          .subscribe(copiedRun => {
            // error handled directly in the HTML file
            copiedRun.original_run_date ?
              this.originalDate.set(copiedRun.original_run_date) :
              this.originalDate.set(data.start_time)
          });
      }
    });
  }

  setInitialValues(): void {
    this.runTime = this.getRunTime(this.validationRun.start_time, this.validationRun.end_time);
    this.errorRate = this.validationRun.total_points !== 0 ?
      (this.validationRun.total_points - this.validationRun.ok_points) / this.validationRun.total_points : 1;
    this.isOwner = this.validationRun.user === this.authService.currentUser.id;
    this.valName.set(this.validationRun.name_tag);
    this.isArchived.set(this.validationRun.is_archived);
    this.expiryDate.set(this.validationRun.expiry_date);
    this.isNearExpiry.set(this.validationRun.is_near_expiry);
  }

  checkIfPublishingInProgress(): void {
    if (this.validationRun.publishing_in_progress || this.publishingInProgress()) {
      this.publishingInProgressInterval = setInterval(() => {
        // no need to handle error here, if this method returns error, nothing will be shown
        this.validationService.getValidationRunById(this.validationRun.id)
          .subscribe(data => {
          if (!data.publishing_in_progress) {
            this.doRefresh.emit(true);
          }
        });
      }, 20 * 1000);

    }
  }

  handlePublishWindow(open: boolean): void {
    this.isPublishingWindowOpen = open;
  }

  startPublishing(): void {
    this.publishingInProgress.set(true)
    this.checkIfPublishingInProgress()
  }

  ngOnDestroy(): void {
    clearInterval(this.publishingInProgressInterval);
  }

}

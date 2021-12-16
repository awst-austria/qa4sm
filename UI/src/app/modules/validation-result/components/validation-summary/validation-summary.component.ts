import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ValidationResultModel} from '../../../../pages/validation-result/validation-result-model';
import {combineLatest, Observable} from 'rxjs';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {FilterService} from '../../../core/services/filter/filter.service';
import {map} from 'rxjs/operators';
import {SCALING_CHOICES} from '../../../scaling/components/scaling/scaling.component';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {AuthService} from '../../../core/services/auth/auth.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {Router} from '@angular/router';


@Component({
  selector: 'qa-validation-summary',
  templateUrl: './validation-summary.component.html',
  styleUrls: ['./validation-summary.component.scss']
})
export class ValidationSummaryComponent implements OnInit {

  @Input() validationModel: ValidationResultModel;
  @Output() doRefresh = new EventEmitter();

  configurations$: Observable<any>;
  validationRun$: Observable<any>;
  dateFormat = 'medium';
  timeZone = 'UTC';
  scalingMethods = SCALING_CHOICES;
  hideElement = true;
  // isCopied: boolean;
  originalDate: Date;

  faIcons = {faArchive: fas.faArchive, faPencil: fas.faPen};

  constructor(private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private filterService: FilterService,
              private globalParamsService: GlobalParamsService,
              private validationService: ValidationrunService,
              private authService: AuthService,
              private router: Router) { }

  ngOnInit(): void {
    // this.isCopied =
    this.updateConfig();
    this.updateValidationRun();
    this.getOriginalDate();
  }

  getCurrentUser(): number {
    return this.authService.currentUser.id;
  }

  private updateConfig(): void{
    this.configurations$ = combineLatest(
      this.validationModel.datasetConfigs,
      this.datasetService.getAllDatasets(),
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
        config =>
          ({...config,
          dataset: datasets.find(ds =>
          config.dataset === ds.id)?.pretty_name,

          version: versions.find(dsVersion =>
          config.version === dsVersion.id).pretty_name,

          variable: variables.find(dsVar =>
          config.variable === dsVar.id).pretty_name,

          filters: config.filters.map(f => dataFilters.find(dsF => dsF.id === f).description),

          parametrisedFilters: config.parametrised_filters.map(f => dataFilters.find(dsF => dsF.id === f).description),

          parametrisedFiltersValues: config.parametrised_filters
            .map(fId => config.parametrisedfilter_set
              .map(pf => [paramFilters.find(pF => pF.id === pf).filter_id, paramFilters
                .find(pF => pF.id === pf).parameters])
              .find(f => f[0] === fId)[1])

          })
      ))
    );
    this.configurations$.subscribe(() => {
    });
  }

  private updateValidationRun(): void{
    this.validationRun$ = this.validationModel.validationRun.pipe(
      map(validation => ({
        ...validation,
        runTime: this.getRunTime(validation.start_time, validation.end_time),
        errorRate: validation.total_points !== 0 ? (validation.total_points - validation.ok_points) / validation.total_points : 1,
        isOwner: validation.user === this.authService.currentUser.id,
      })),
    );
  }

  getRunTime(startTime: Date, endTime: Date): number{
    const startTimeDate = new Date(startTime);
    const endTimeDate = new Date(endTime);
    const runTime = endTimeDate.getTime() - startTimeDate.getTime();
    return Math.round(runTime / 60000);
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  toggleEditing(): void{
    this.hideElement = !this.hideElement;
  }
  saveName(validationId: string, newName: string): void{
    this.validationService.saveResultsName(validationId, newName).subscribe(
      () => {
        this.doRefresh.emit(true);
      });

  }

  refresh(dorefresh: boolean): void{
    if (dorefresh){
      this.ngOnInit();
    } else {
      this.router.navigate(['/my-validations']);
    }
  }

  getOriginalDate(): void{
    this.validationModel.validationRun.subscribe(data => {
      if (data.is_a_copy){
        this.validationService.getCopiedRunRecord(data.id).subscribe(copiedRun => {
          if (copiedRun.original_run_date){
            this.originalDate = copiedRun.original_run_date;
          } else {
            this.originalDate = data.start_time;
          }
        });
      }
    });
  }
}

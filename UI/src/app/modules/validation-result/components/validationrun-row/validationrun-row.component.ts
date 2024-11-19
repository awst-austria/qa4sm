import {Component, EventEmitter, Input, OnDestroy, OnInit, Output, signal, SimpleChanges} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from 'src/app/modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from 'src/app/modules/core/services/dataset/dataset-variable.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {combineLatest, EMPTY, Observable, Observer, of} from 'rxjs';
import {catchError, map} from 'rxjs/operators';
import {ValidationRunConfigService} from '../../../../pages/validate/service/validation-run-config.service';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {ToastService} from '../../../core/services/toast/toast.service';

export interface FilterPayload {
  statuses: string[];
  name: string;
  selectedDates: [Date, Date];
  prettyName: string;
}

@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit, OnDestroy {

  @Input() published = false;
  @Input() validationRun: ValidationrunDto;
  @Input() isVisible: boolean = true;  // Default visibility is true (visible)
  @Input() filterPayload: FilterPayload | null = null;
  @Output() matchesFilter = new EventEmitter<boolean>();

  @Output() emitError = new EventEmitter();

  rowVisibility: Map<string, boolean> = new Map();

  configurations$: Observable<any>;
  validationStatusInterval: any;
  validationStatus = signal<string | undefined>(undefined);

  dateFormat = 'medium';
  timeZone = 'UTC';
  faIcons = {faArchive: fas.faArchive, faPencil: fas.faPen};
  hideElement = true;
  originalDate = signal<Date | undefined>(undefined)
  valName = signal<string | undefined>(undefined);

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              public globalParamsService: GlobalParamsService,
              private validationService: ValidationrunService,
              public validationConfigService: ValidationRunConfigService,
              public toastService: ToastService) {
  }

  ngOnInit(): void {
    if (this.validationRun.is_a_copy) {
      this.getOriginalDate(this.validationRun);
    }
    this.updateConfig();
    this.valName.set(this.validationRun.name_tag);
    this.validationStatus.set(this.getStatusFromProgress(this.validationRun));
    this.refreshStatus();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.filterPayload && this.filterPayload) {
      this.updateConfig();
    }
  }

  private updateConfig(): void {
    this.configurations$ = combineLatest(
      [
        this.datasetConfigService.getConfigByValidationrun(this.validationRun.id),
        this.datasetService.getAllDatasets(true, false),
        this.datasetVersionService.getAllVersions().pipe(
          catchError(() => of([]))
        ),
        this.datasetVariableService.getAllVariables().pipe(
          catchError(() => of([]))
        )
      ]
    ).pipe(
      map(([configurations, datasets, versions, variables]) =>
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
            }
          }
        )
      ),
      map(configurations => {
        // Emit whether any configuration matches the dataset filter passed
        const matches = configurations.some(config =>
          this.filterPayload?.prettyName
            ? config.dataset?.includes(this.filterPayload.prettyName)
            : true
        );
        this.matchesFilter.emit(matches);
        return configurations;
      }),
      catchError(() => {
        this.emitError.emit(true);
        return EMPTY
      })
    );
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  handleRowFilter(id: string, matches: boolean): void {
    this.rowVisibility.set(id, matches);
  }

  getStatusFromProgress(valrun): string {
    let status: string;
    if (valrun.progress === 0 && valrun.end_time === null) {
      status = 'Scheduled';
    } else if (valrun.progress === 100 && valrun.end_time) {
      status = 'Done';
    } else if (valrun.progress === -1 || valrun.progress === -100) {
      status = 'Cancelled';
    } else if (valrun.end_time != null || valrun.total_points == 0) {
      status = 'ERROR';
    } else {
      status = 'Running' + ' ' + `${valrun.progress}%`;
    }
    return status;
  }

  toggleEditing(): void {
    this.hideElement = !this.hideElement;
  }

  saveNameObserver = (newName: string): Observer<any> => {
    return {
      next: () => this.onSaveNameNext(newName),
      error: (error: CustomHttpError) =>
        this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message),
      complete: () => this.toastService.showSuccess('Name updated')
    }
  }

  onSaveNameNext(newName): void {
    this.valName.set(newName);
    this.toggleEditing();
  }

  saveName(validationId: string, newName: string): void {
    this.validationService.saveResultsName(validationId, newName)
      .subscribe(this.saveNameObserver(newName));
  }


  getOriginalDate(copiedRun: ValidationrunDto): void {
    // error handled in the HTML file
    this.validationService.getCopiedRunRecord(copiedRun.id)
      .subscribe(data => {
        data.original_run_date ?
          this.originalDate.set(data.original_run_date) :
          this.originalDate.set(copiedRun.start_time);
      });
  }

  refreshStatus(): void {
    if (
      (this.validationRun.progress !== -1 && this.validationRun.progress !== -100) &&
      !(this.validationRun.progress === 100 &&
        this.validationRun.end_time !== null) &&
      !(this.validationRun.progress === 0 &&
        this.validationRun.end_time !== null)) {
      this.validationStatusInterval = setInterval(() => {
        this.validationService.getValidationRunById(this.validationRun.id)
          .pipe(
            catchError(() => {
              this.validationStatus.set('Unknown');
              clearInterval(this.validationStatusInterval);
              return EMPTY
            })
          )
          .subscribe(data => {
            this.validationStatus.set(this.getStatusFromProgress(data));
            if (data.progress === 100 && data.end_time) {
              this.validationService.refreshComponent(this.validationRun.id);
            }
          });
      }, 60 * 1000); // one minute
    }
  }

  ngOnDestroy(): void {
    clearInterval(this.validationStatusInterval);
  }

}

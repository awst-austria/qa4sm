import {Component, EventEmitter, Input, OnDestroy, OnInit, Output} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from 'src/app/modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from 'src/app/modules/core/services/dataset/dataset-variable.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {BehaviorSubject, combineLatest, Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {ValidationRunConfigService} from '../../../../pages/validate/service/validation-run-config.service';


@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit, OnDestroy {

  @Input() published = false;
  @Input() validationRun: ValidationrunDto;
  @Output() doRefresh = new EventEmitter();
  configurations$: Observable<any>;
  validationStatus: any;
  validationStatus$: BehaviorSubject<string> = new BehaviorSubject<string>('');

  dateFormat = 'medium';
  timeZone = 'UTC';
  faIcons = {faArchive: fas.faArchive, faPencil: fas.faPen};
  hideElement = true;
  originalDate: Date;
  valName$: BehaviorSubject<string> = new BehaviorSubject<string>('');

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              public globalParamsService: GlobalParamsService,
              private validationService: ValidationrunService,
              public validationConfigService: ValidationRunConfigService,) {
  }

  ngOnInit(): void {
    if (this.validationRun.is_a_copy) {
      this.getOriginalDate(this.validationRun);
    }
    this.updateConfig();
    this.valName$.next(this.validationRun.name_tag);
    this.validationStatus$.next(this.getStatusFromProgress(this.validationRun));
    this.refreshStatus();
  }

  private updateConfig(): void {
    this.configurations$ = combineLatest(
      this.datasetConfigService.getConfigByValidationrun(this.validationRun.id),
      this.datasetService.getAllDatasets(true, false),
      this.datasetVersionService.getAllVersions(),
      this.datasetVariableService.getAllVariables()
    ).pipe(
      map(([configurations, datasets, versions, variables]) =>
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
            }
          }
        )
      )
    );
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  getStatusFromProgress(valrun): string {
    let status: string;
    if (valrun.progress === 0 && valrun.end_time === null) {
      status = 'Scheduled';
    } else if (valrun.progress === 100 && valrun.end_time) {
      status = 'Done';
    }
    else if (valrun.progress === -1) {
      status = 'Cancelled';
    } else if (valrun.end_time != null || valrun.total_points == 0) {
      status = 'ERROR';
    } else {
      status = 'Running' + ' ' + `${valrun.progress}%`;
    }
    return status;
  }

  toggleEditing(): void{
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

  getOriginalDate(copiedRun: ValidationrunDto): void {
    this.validationService.getCopiedRunRecord(copiedRun.id).subscribe(data => {
      if (data.original_run_date){
        this.originalDate = data.original_run_date;
      } else{
        this.originalDate = copiedRun.start_time;
      }
    });
  }

  refreshStatus(): void{
    if (
      (this.validationRun.progress !== -1) &&
      !(this.validationRun.progress === 100 &&
        this.validationRun.end_time !== null) &&
      !(this.validationRun.progress === 0 &&
        this.validationRun.end_time !== null)){
      this.validationStatus = setInterval(() => {
        this.validationService.getValidationRunById(this.validationRun.id).subscribe(data => {
          this.validationStatus$.next(this.getStatusFromProgress(data));
          if (data.progress === 100 && data.end_time) {
            this.validationService.refreshComponent(this.validationRun.id);
          }
        });
      }, 60 * 1000); // one minute
    }
  }

  ngOnDestroy(): void {
    clearInterval(this.validationStatus);
  }

}

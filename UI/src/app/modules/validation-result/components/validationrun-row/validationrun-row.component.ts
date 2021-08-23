import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from 'src/app/modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from 'src/app/modules/core/services/dataset/dataset-variable.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {combineLatest, Observable} from 'rxjs';
import {map} from 'rxjs/operators';


@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit {

  @Input() published: boolean = false;
  @Input() validationRun: ValidationrunDto;
  configurations$: Observable<any>;

  dateFormat = 'medium';
  timeZone = 'UTC';
  faIcons = {faArchive: fas.faArchive, faPencil: fas.faPen};
  hideElement = true;

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private globalParamsService: GlobalParamsService,
              private validationService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.updateConfig();
  }

  private updateConfig(): void{
    this.configurations$ = combineLatest(
      this.datasetConfigService.getConfigByValidationrun(this.validationRun.id),
      this.datasetService.getAllDatasets(),
      this.datasetVersionService.getAllVersions(),
      this.datasetVariableService.getAllVariables()
    ).pipe(
      map(([configurations, datasets, versions, variables]) =>
        configurations.map(
          config =>
            ({...config,
              dataset:  datasets.find(ds =>
                config.dataset === ds.id)?.pretty_name,

              version: versions.find(dsVersion =>
                config.version === dsVersion.id).pretty_name,

              variable: variables.find(dsVar =>
                config.variable === dsVar.id).pretty_name,
            })
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
    } else if (valrun.progress === 100 && valrun.end_time){
      status = 'Done';
    } else if (valrun.progress === -1) {
      status = 'Cancelled';
    } else if (valrun.end_time != null) {
      status = 'ERROR';
    } else {
      status = 'Running' + ' ' + `${valrun.progress}%`;
    }
    return status;
  }

  toggleEditing(): void{
    this.hideElement = !this.hideElement;
  }
  saveName(validationId: string, newName: string): void{
    this.validationService.saveResultsName(validationId, newName).subscribe(
      () => {
        this.validationService.refreshComponent(validationId);
      });
    // window.location.reload();
  }
}

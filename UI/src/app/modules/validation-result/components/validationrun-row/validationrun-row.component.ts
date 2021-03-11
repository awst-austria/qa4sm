import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/gloabal-params/global-params.service';
import {ValidationRunRowModel} from './validation-configuration-model';
import {DatasetRowModel} from './dataset-row.model';
import {DatasetService} from 'src/app/modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from 'src/app/modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from 'src/app/modules/core/services/dataset/dataset-variable.service';
import {fas} from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit {

  @Input() published: boolean = false;
  @Input() validationRun: ValidationrunDto;

  model: ValidationRunRowModel;
  dateFormat = 'MMM. dd, YYYY, hh:mm a O';
  timeZone = 'UTC';
  faIcons = {faArchive: fas.faArchive};

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private globalParamsService: GlobalParamsService) {
  }

  ngOnInit(): void {
    this.model = new ValidationRunRowModel(this.validationRun, [], new DatasetRowModel());
    this.loadRowData();
  }

  private loadRowData() {
    this.datasetConfigService.getConfigByValidationrun(this.model.validationRun.id).subscribe(configs => {
      configs.forEach(config => {
        let dataset$ = this.datasetService.getDatasetById(config.dataset);
        let datasetVersion$ = this.datasetVersionService.getVersionById(config.version);
        let datasetVariable$ = this.datasetVariableService.getVariableById(config.variable);
        let datasetRowModel = new DatasetRowModel(dataset$, datasetVersion$, datasetVariable$);

        if (this.model.validationRun.reference_configuration === config.id) {
          this.model.referenceRow = datasetRowModel;
        } else {
          this.model.datasetRows.push(datasetRowModel);
        }
      });
    });
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
    }
    return status;
  }

}

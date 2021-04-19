import {Component, Input, OnInit, ViewEncapsulation} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetConfigurationDto} from '../../services/dataset-configuration.dto';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';

@Component({
  selector: 'qa-summary-statistics',
  templateUrl: './summary-statistics.component.html',
  styleUrls: ['./summary-statistics.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class SummaryStatisticsComponent implements OnInit {
  @Input() validationRun: ValidationrunDto;
  @Input() configs: DatasetConfigurationDto[];
  table$: Observable<string>;
  refConfig: DatasetConfigurationDto;
  refDataset$: Observable<DatasetDto>;
  refDatasetVersion$: Observable<DatasetVersionDto>;
  refDatasetVariable$: Observable<DatasetVariableDto>;

  constructor(private validationService: ValidationrunService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService) {
  }

  ngOnInit(): void {
    this.getSummaryStatistics();
    this.getRefConfig();
  }

  getSummaryStatistics(): void {
    const parameters = new HttpParams().set('id', this.validationRun.id);
    this.table$ = this.validationService.getSummaryStatistics(parameters);
  }

  getRefConfig(): void{
    this.refConfig = this.configs.find(config => config.id === this.validationRun.reference_configuration);
    this.refDataset$ = this.datasetService.getDatasetById(this.refConfig.dataset);
    this.refDatasetVersion$ = this.datasetVersionService.getVersionById(this.refConfig.version);
    this.refDatasetVariable$ = this.datasetVariableService.getVariableById(this.refConfig.variable);
  }

  getSummaryStatisticsAsCsv(): void{
    this.validationService.downloadSummaryStatisticsCsv(this.validationRun.id);
  }


}

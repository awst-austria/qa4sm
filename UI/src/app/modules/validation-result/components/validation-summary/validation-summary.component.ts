import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {ValidationResultModel} from '../../../../pages/validation-result/validation-result-model';
import {DatasetConfigurationDto} from '../../services/dataset-configuration.dto';
import {Observable} from 'rxjs';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {DatasetSummaryModel} from './dataset-summary.model';
import {FilterDto} from '../../../core/services/filter/filter.dto';
import {FilterService} from '../../../core/services/filter/filter.service';
import {ValidationSummaryModel} from './validation-summary.model';

@Component({
  selector: 'qa-validation-summary',
  templateUrl: './validation-summary.component.html',
  styleUrls: ['./validation-summary.component.scss']
})
export class ValidationSummaryComponent implements OnInit {

  @Input() validationModel: ValidationResultModel;

  valrun$: Observable<ValidationrunDto>;
  validationRun: ValidationrunDto;
  configuration: Observable<DatasetConfigurationDto[]>;
  model: ValidationSummaryModel;
  numberOfDatasetsCompared: number;
  dateFormat = 'MMM. dd, YYYY, hh:mm a O';
  timeZone = 'UTC';

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private filterService: FilterService) { }

  ngOnInit(): void {
    this.valrun$ = this.validationModel.validationRun;
    this.configuration = this.validationModel.datasetConfigs;
    this.getValidationSummary();

  }

  // private getNumberOfDatasetsCompared() {
  //   this.datasetConfigService.getConfigByValidationrun(this.valrun?.id).subscribe(configs => {
  //     this.numberOfDatasetsCompared = configs.length;
  //     console.log(configs, configs.length);
  //   });
  // }
  private getValidationSummary(): void{
    this.valrun$.subscribe(validationrun => {
      this.validationRun = validationrun;
    });
    this.model = new ValidationSummaryModel(this.validationRun, [], new DatasetSummaryModel());
    this.configuration.subscribe(configs => {
      this.numberOfDatasetsCompared = configs.length;
      configs.forEach(config => {
        let dataset$ = this.datasetService.getDatasetById(config.dataset);
        let datasetVersion$ = this.datasetVersionService.getVersionById(config.version);
        let datasetVariable$ = this.datasetVariableService.getVariableById(config.variable);
        let filters = this.getUsedFilters(config.filters);
        console.log(config.parametrised_filters);
        // let filters = this.filterService.getFiltersByDatasetId(config.)
        let datasetSummaryModel = new DatasetSummaryModel(dataset$, datasetVersion$, datasetVariable$, filters);

        if (this.model.validationRun?.reference_configuration === config.id) {
          this.model.referenceRow = datasetSummaryModel;
        } else {
          this.model.datasetSummary.push(datasetSummaryModel);
        }
      });
    });
  }

  private getUsedFilters(filtersId: any): FilterDto[]{
    const filtersArray: FilterDto[] = [];
    filtersId.forEach(filterId => {
      this.filterService.getFilterById(filterId).subscribe(filter => {
        filtersArray.push(filter);
      });
    });
    return filtersArray;
  }

}

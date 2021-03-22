import {Component, Input, OnInit} from '@angular/core';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {ValidationResultModel} from '../../../../pages/validation-result/validation-result-model';
import {combineLatest, Observable} from 'rxjs';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {FilterDto} from '../../../core/services/filter/filter.dto';
import {FilterService} from '../../../core/services/filter/filter.service';
import {map} from 'rxjs/operators';

@Component({
  selector: 'qa-validation-summary',
  templateUrl: './validation-summary.component.html',
  styleUrls: ['./validation-summary.component.scss']
})
export class ValidationSummaryComponent implements OnInit {

  @Input() validationModel: ValidationResultModel;

  configurations$: Observable<any>;
  dateFormat = 'MMM. dd, YYYY, hh:mm a O';
  timeZone = 'UTC';

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private filterService: FilterService) { }

  ngOnInit(): void {
    this.getFullConfig();
  }

  private getFullConfig(): void{
    this.configurations$ = combineLatest(
      this.validationModel.datasetConfigs,
      this.datasetService.getAllDatasets(),
      this.datasetVersionService.getAllVersions(),
      this.datasetVariableService.getAllVariables()
    ).pipe(
      map(([configurations,
             datasets,
             versions,
             variables]) =>
      configurations.map(
        config =>
          ({...config,
          dataset: datasets.find(ds =>
          config.dataset === ds.id)?.pretty_name,

          version: versions.find(dsVersion =>
          config.version === dsVersion.id).pretty_name,

          variable: variables.find(dsVar =>
          config.variable === dsVar.id).pretty_name
          })
      ))
    );
    this.configurations$.subscribe(data => {
      console.log(data);
    });
    console.log(this.configurations$);
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

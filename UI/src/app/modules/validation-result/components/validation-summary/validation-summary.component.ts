import {Component, Input, OnInit} from '@angular/core';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {ValidationResultModel} from '../../../../pages/validation-result/validation-result-model';
import {combineLatest, Observable} from 'rxjs';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {FilterService} from '../../../core/services/filter/filter.service';
import {map} from 'rxjs/operators';
import {SCALING_CHOICES} from '../../../scaling/components/scaling/scaling.component';


@Component({
  selector: 'qa-validation-summary',
  templateUrl: './validation-summary.component.html',
  styleUrls: ['./validation-summary.component.scss']
})
export class ValidationSummaryComponent implements OnInit {

  @Input() validationModel: ValidationResultModel;

  configurations$: Observable<any>;
  dateFormat = 'medium';
  timeZone = 'UTC';
  scalingMethods = SCALING_CHOICES;

  constructor(private datasetConfigService: DatasetConfigurationService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private filterService: FilterService) { }

  ngOnInit(): void {
    this.getFullConfig();
    console.log(this.configurations$);
    this.filterService.getParameterisedFilterById(1490).subscribe(data =>
      console.log(data));
    console.log(this.scalingMethods[0]);
  }

  private getFullConfig(): void{
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
    this.configurations$.subscribe(data => {
      console.log(data);
    });
  }
}

import {Component, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {

  comparisonTable$: Observable<string>;
  // need to connect comparisonModel to metrics for showing and validation ids
  private comparisonMetrics$: Observable<{ metric_pretty_name: string; metric_query_name: string; comparison_plots: any }[]>;

  constructor(private comparisonService: ComparisonService) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
        this.getComparisonMetrics(comparison);
      }
    });
  }

  getComparisonMetrics(comparisonModel: Validations2CompareModel): void {
    // get all the available metrics in the MetricsComparisonDto format
    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    // TODO: is this correct?
    let parameters = new HttpParams().set('get_intersection', String(comparisonModel.getIntersection).toString());
    ids.forEach(id => {
      parameters = parameters.append('ids', id);
    });
    const comparisonMetrics = [];
    this.comparisonService.getMetrics4Comparison(parameters).subscribe(response => {
      if (response) {
        response.forEach(metric => {
          comparisonMetrics.push(metric.metric_query_name);
        });
        this.getComparisonTable(comparisonMetrics, comparisonModel);
      }
    });
  }

  getComparisonTable(metricList: string[], comparisonModel: Validations2CompareModel): void {
    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    let parameters = new HttpParams().set('get_intersection', comparisonModel.getIntersection.toString());
    ids.forEach(id => {
      parameters = parameters.append('ids', id);
    });
    metricList.forEach(metric => {
      parameters = parameters.append('metric_list', metric);
    });
    // console.log(metricList)
    // console.log('parameters', parameters)
    console.log('table', this.comparisonService.getComparisonTable(parameters));
    this.comparisonTable$ = this.comparisonService.getComparisonTable(parameters);
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    this.comparisonService.downloadComparisonTableCsv(
      null, null, null, null
    );
  }
}

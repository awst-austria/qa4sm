import {Component, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {debounceTime} from 'rxjs/operators';

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {

  comparisonTable$: Observable<string>;

  constructor(private comparisonService: ComparisonService) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.pipe(debounceTime(2000)).subscribe(comparison => {
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
    this.comparisonTable$ = this.comparisonService.getComparisonTable(parameters);
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    this.comparisonService.downloadComparisonTableCsv(
      null, null, null, null
    );
  }
}

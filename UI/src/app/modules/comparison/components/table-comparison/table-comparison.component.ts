import {Component, Input, OnInit, SimpleChanges} from '@angular/core';
import {ComparisonService} from "../../services/comparison.service";
import {Observable} from "rxjs";
import {MetricModel} from "../../../metrics/components/metric/metric-model";
import {HttpParams} from "@angular/common/http";
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {map} from "rxjs/operators";
import {MetricsComparisonDto} from "../../services/metrics-comparison.dto";

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {

  @Input() comparisonModel: Validations2CompareModel;
  comparisonTable$: Observable<string>;
  comparisonMetrics: string[] = []
  // need to connect comparisonModel to metrics for showing and validation ids
  private comparisonMetrics$: Observable<{ metric_pretty_name: string; metric_query_name: string; comparison_plots: any }[]>;

  constructor(private comparisonService: ComparisonService,) { }

  ngOnInit(): void {
  }

  ngOnChanges(changes: SimpleChanges){
    // change according to the model, unless it's undefined
    if(this.comparisonModel){this.getComparisonMetrics()}
  }

  getComparisonMetrics(): void {
    // get all the available metrics in the MetricsComparisonDto format
    const ids = this.comparisonService.getValidationsIds(this.comparisonModel.selectedValidations);
    let parameters = new HttpParams().set('get_intersection', String(this.comparisonModel.getIntersection).toString());  // TODO: is this correct?
    ids.forEach(id => {parameters = parameters.append('ids', id)});

    this.comparisonService.getMetrics4Comparison(parameters).subscribe(response => {
      if (response) {
        response.forEach(metric => {
          this.comparisonMetrics.push(metric.metric_query_name)});
        this.getComparisonTable(this.comparisonMetrics);
      }
    })
  }

  getComparisonTable(metric_list: string[]): void {
    const ids = this.comparisonService.getValidationsIds(this.comparisonModel.selectedValidations);
    let parameters = new HttpParams().set('get_intersection', this.comparisonModel.getIntersection.toString());
    ids.forEach(id => {parameters = parameters.append('ids', id)});
    metric_list.forEach(metric => {parameters = parameters.append('metric_list', metric)});
    // console.log(metric_list)
    // console.log('parameters', parameters)
    console.log('table', this.comparisonService.getComparisonTable(parameters))
    this.comparisonTable$ = this.comparisonService.getComparisonTable(parameters);
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    this.comparisonService.downloadComparisonTableCsv(
      null, null,null,null
    );
  }
}

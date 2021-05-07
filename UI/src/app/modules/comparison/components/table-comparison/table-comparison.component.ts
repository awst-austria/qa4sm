import {Component, Input, OnInit} from '@angular/core';
import {ComparisonService} from "../../services/comparison.service";
import {Observable} from "rxjs";
import {MetricModel} from "../../../metrics/components/metric/metric-model";
import {HttpParams} from "@angular/common/http";
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {map} from "rxjs/operators";

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {

  @Input() comparisonModel: Validations2CompareModel;
  comparisonTable$: Observable<string>;
  // need to connect comparisonModel to metrics for showing and validation ids
  private comparisonMetrics$: Observable<{ metric_pretty_name: string; metric_query_name: string; comparison_plots: any }[]>;

  constructor(private comparisonService: ComparisonService,) { }

  ngOnInit(): void {
  }

  getComparisonMetrics() {
    // get all the available metrics for this particular comparison configuration
    const ids = this.comparisonService.getValidationsIds(this.comparisonModel.selectedValidations);
    const params = new HttpParams().set('ids', String(ids));
    this.comparisonMetrics$ = this.comparisonService.getMetrics4Comparison(params).pipe(
      map((metrics) =>
        metrics.map(
          metric =>
            ({
              ...metric,
              comparison_plots: null
            })
        )
      )
    )
    // let metrics = []
    // for (let metric of this.comparisonMetrics$){
    //   metrics.push(metric.metric_query_name)
    // }
    // return metrics
  }

  getComparisonTable(): void {
    const metric_list = this.getComparisonMetrics()
    const parameters = new HttpParams()
      .set('ids', null)
      .set('metric_list', String(metric_list))  // How to pass list??
      .set('get_intersection', null);
    this.comparisonTable$ = this.comparisonService.getComparisonTable(parameters);
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    this.comparisonService.downloadComparisonTableCsv(
      null, null,null,null
    );
  }
}

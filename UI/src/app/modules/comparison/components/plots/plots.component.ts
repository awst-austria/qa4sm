import {Component, Input, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {MetricModel} from "../../../metrics/components/metric/metric-model";
import {MetricsComparisonDto} from "../../services/metrics-comparison.dto";
import {map} from "rxjs/operators";
import {DomSanitizer, SafeUrl} from "@angular/platform-browser";

// types of plots to show up. Shouldn't be hardcoded
const PLOT_TYPES =  ['boxplot', 'correlation', 'difference', 'mapplot'];

@Component({
  selector: 'qa-plots',
  templateUrl: './plots.component.html',
  styleUrls: ['./plots.component.scss'],
})
export class PlotsComponent implements OnInit {

  @Input() comparisonModel: Validations2CompareModel;
  // metrics to show the table/plots for
  comparisonMetrics$: Observable<{
    metric_pretty_name: string;
    metric_query_name: string;
    comparison_plots: Observable<string[]> }[]>
  selectedMetric: MetricsComparisonDto
  // for showing the plots
  plotPrefix = 'data:image/png;base64,';

  constructor(private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer) {
  }

  ngOnInit(): void {
    this.getComparisonMetrics();
  }

  getComparisonPlots(metric:string): Observable<string[]> {
    const parameters = new HttpParams()
      .set('ids', String(this.comparisonModel.selectedValidations))
      .set('plot_types', String(PLOT_TYPES))  // should be list instead?
      .set('metric', metric)
      .set('get_intersection', String(this.comparisonModel.getIntersection))
      .set('extent', null);

    return this.comparisonService.getComparisonPlots(parameters);
  }

  getComparisonMetrics(): void {
    // get all the available metrics for this particular comparison configuration
    const ids = this.comparisonService.getValidationsIds(this.comparisonModel.selectedValidations);
    const params = new HttpParams().set('ids', String(ids));
    this.comparisonMetrics$ = this.comparisonService.getMetrics4Comparison(params).pipe(
      map((metrics) =>
        metrics.map(
          metric =>
            ({
              ...metric,
              comparison_plots: this.getComparisonPlots(metric.metric_query_name)
            })
        )
      )
    )
    this.selectedMetric = this.comparisonMetrics$[0]
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.domSanitizer.bypassSecurityTrustUrl(this.plotPrefix + plotBase64);
  }

  downloadResultFiles(): void {
    // download all the shown images as .png
  }
}

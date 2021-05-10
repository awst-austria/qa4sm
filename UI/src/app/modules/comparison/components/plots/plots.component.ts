import {Component, Input, OnInit, SimpleChanges} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {MetricsComparisonDto} from "../../services/metrics-comparison.dto";
import {DomSanitizer, SafeUrl} from "@angular/platform-browser";
import {Observable} from "rxjs";

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
  comparisonMetrics: MetricsComparisonDto[] = []
  selectedMetric: MetricsComparisonDto
  // for showing the plots
  plotPrefix = 'data:image/png;base64,';
  // metric-relative plots
  metricPlots$: Observable<string[]>;

  constructor(private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer) {
  }

  ngOnInit(): void {
  }

  ngOnChanges(changes: SimpleChanges){
    // change according to the model, unless it's undefined
    // console.log('changes', changes)
    if(this.comparisonModel){this.getComparisonMetrics()}
  }

  getComparisonMetrics(): void {
    // get all the available metrics in the MetricsComparisonDto format
    const ids = this.comparisonService.getValidationsIds(this.comparisonModel.selectedValidations);
    let params = new HttpParams().set('get_intersection', String(this.comparisonModel.getIntersection));
    ids.forEach(id => {params = params.append('ids', id)});

    this.comparisonService.getMetrics4Comparison(params).subscribe(response => {
        if (response) {
          response.forEach(metric => {
            this.comparisonMetrics.push(
              new MetricsComparisonDto(metric.metric_query_name, metric.metric_pretty_name))
          })
          this.selectedMetric = this.comparisonMetrics[0];
          this.getComparisonPlots(this.selectedMetric.metric_query_name)
        }}
    )}

  getComparisonPlots(metric:string): void {
    // Get all the plots for a specific comparison and metric
    let plots = []
    let parameters = new HttpParams()
      .set('metric', metric)
      .set('get_intersection', String(this.comparisonModel.getIntersection));  // TODO: is this correct?

    let ids = this.comparisonService.getValidationsIds(this.comparisonModel.selectedValidations)
    ids.forEach(id => {parameters = parameters.append('ids', id)});
    PLOT_TYPES.forEach(plotType => {parameters = parameters.append('plot_types', plotType)});
    console.log('plots', this.comparisonService.getComparisonPlots(parameters))
    this.metricPlots$ = this.comparisonService.getComparisonPlots(parameters)
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.domSanitizer.bypassSecurityTrustUrl(this.plotPrefix + plotBase64);
  }

  downloadResultFiles(): void {
    // download all the shown images as .png
  }
}

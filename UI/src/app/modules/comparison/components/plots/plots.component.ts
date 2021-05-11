import {Component, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {MetricsComparisonDto} from '../../services/metrics-comparison.dto';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';
import {Observable} from 'rxjs';

// types of plots to show up. Shouldn't be hardcoded
const PLOT_TYPES = ['boxplot', 'correlation', 'difference', 'mapplot'];

@Component({
  selector: 'qa-plots',
  templateUrl: './plots.component.html',
  styleUrls: ['./plots.component.scss'],
})
export class PlotsComponent implements OnInit {
  selectedMetric: MetricsComparisonDto;
  // for showing the plots
  plotPrefix = 'data:image/png;base64,';
  // metric-relative plots
  metricPlots$: Observable<string[]>;
  metricsErrorMessage: string;

  constructor(private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer) {
  }

  ngOnInit(): void {
    this. startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
        this.getComparisonMetrics(comparison);
      }
    });
  }

  getComparisonMetrics(comparisonModel: Validations2CompareModel): void {
    // get all the available metrics in the MetricsComparisonDto format and initialize plots for a metric
    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    let params = new HttpParams();
    params = params.append('get_intersection', String(comparisonModel.getIntersection));
    // let params = new HttpParams().set('get_intersection', String(comparisonModel.getIntersection));
    ids.forEach(id => {
      params = params.append('ids', id);
    });

    this.comparisonService.getMetrics4Comparison(params).subscribe(response => {
      const comparisonMetrics = [];
      if (response && response.length > 1) {
        response.forEach(metric => {
          comparisonMetrics.push(
            new MetricsComparisonDto(metric.metric_query_name, metric.metric_pretty_name));
        });
        this.selectedMetric = comparisonMetrics[0];
        this.getComparisonPlots(this.selectedMetric.metric_query_name, comparisonModel);
      } else {
        this.metricsErrorMessage = response[0].message; // this message can be shown somewhere so users know what is wrong
        console.log(response[0].message);
      }
    });
  }

  getComparisonPlots(metric: string, comparisonModel: Validations2CompareModel): void {
    // Get all the plots for a specific comparison and metric
    let parameters = new HttpParams()
      .set('metric', metric)
      .set('get_intersection', String(comparisonModel.getIntersection));

    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    ids.forEach(id => {
      parameters = parameters.append('ids', id);
    });
    PLOT_TYPES.forEach(plotType => {
      parameters = parameters.append('plot_types', plotType);
    });
    console.log('plots', this.comparisonService.getComparisonPlots(parameters));
    this.metricPlots$ = this.comparisonService.getComparisonPlots(parameters);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.domSanitizer.bypassSecurityTrustUrl(this.plotPrefix + plotBase64);
  }

  downloadResultFiles(): void {
    // download all the shown images as .png
  }
}

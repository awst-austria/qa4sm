import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {MetricsComparisonDto} from '../../services/metrics-comparison.dto';
import {SafeUrl} from '@angular/platform-browser';
import {PlotDto} from '../../../core/services/global/plot.dto';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {ExtentModel} from '../spatial-extent/extent-model';
import {catchError, debounceTime} from 'rxjs/operators';
import {EMPTY, Observable} from 'rxjs';

// types of plots to show up. Shouldn't be hardcoded
const PLOT_TYPES = ['boxplot', 'mapplot'];

@Component({
  selector: 'qa-plots',
  templateUrl: './plots.component.html',
  styleUrls: ['./plots.component.scss'],
})

export class PlotsComponent implements OnInit {
  @Output() isError = new EventEmitter<boolean>();
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [],
    new ExtentModel(true).getIntersection,
    false
  );
  // metrics to show the table/plots for
  comparisonMetrics: MetricsComparisonDto[] = [];
  selectedMetric: MetricsComparisonDto;
  metricsErrorMessage: string;
  showLoadingSpinner = true;
  errorHappened = false;
  plots: PlotDto[];

  displayGallery: boolean;
  activeIndex = 0;

  getComparisonPlotsObserver = {
    next: data => this.onGetComparisonPlotsNext(data),
    error: () => this.onGetComparisonPlotsError()
  }

  constructor(private comparisonService: ComparisonService,
              private plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.pipe(debounceTime(5000)).subscribe(comparison => {
      this.comparisonModel = comparison;
      if ((comparison.selectedValidations.length > 1 && !comparison.multipleNonReference) ||
        (comparison.selectedValidations.length === 1 && comparison.multipleNonReference)) {
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
    this.comparisonMetrics = [];
    this.comparisonService.getMetrics4Comparison(params)
      .pipe(
        catchError(err => {
          return this.getComparisonMetricsErrorHandler(err)
        })
      )
      .subscribe(
      response => {
        if (response && response.length > 1) {
          response.forEach(metric => {
            this.comparisonMetrics.push(
              new MetricsComparisonDto(metric.metric_query_name, metric.metric_pretty_name));
          });
          this.selectedMetric = this.comparisonMetrics[0];
          this.getComparisonPlots(this.selectedMetric.metric_query_name, comparisonModel);
        }
      });
  }

  getComparisonMetricsErrorHandler(err: string): Observable<never>{
    this.metricsErrorMessage = err;
    this.errorHappened = true;
    this.showLoadingSpinner = false;
    return EMPTY
  }

  showGallery(index: number = 0): void {
    this.activeIndex = index;
    this.displayGallery = true;
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

    this.comparisonService.getComparisonPlots(parameters).subscribe(
      this.getComparisonPlotsObserver
    );
  }

  private onGetComparisonPlotsNext(data): void {
    if (data) {
      this.plots = data;
      this.showLoadingSpinner = false;
    }
  }

  private onGetComparisonPlotsError(): void {
    this.showLoadingSpinner = false;
    this.errorHappened = true;
    this.isError.emit(true);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

  onMetricChange(): void {
    this.getComparisonPlots(this.selectedMetric.metric_query_name, this.comparisonModel);
  }

}

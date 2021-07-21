import {Component, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {MetricsComparisonDto} from '../../services/metrics-comparison.dto';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';
import {Observable} from 'rxjs';
import {PlotDto} from '../../../core/services/global/plot.dto';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {ExtentModel} from '../spatial-extent/extent-model';
import {CarouselComponent} from 'angular-gallery/lib/carousel.component.d';
import {Gallery} from 'angular-gallery';
import {debounceTime} from "rxjs/operators";

// types of plots to show up. Shouldn't be hardcoded
const PLOT_TYPES = ['boxplot', 'mapplot'];

@Component({
  selector: 'qa-plots',
  templateUrl: './plots.component.html',
  styleUrls: ['./plots.component.scss'],
})

export class PlotsComponent implements OnInit {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [],
    new ExtentModel(true).getIntersection,
  );
  // metrics to show the table/plots for
  comparisonMetrics: MetricsComparisonDto[] = [];
  selectedMetric: MetricsComparisonDto;
  // metric-relative plots
  metricPlots$: Observable<PlotDto[]>;
  metricsErrorMessage: string;

  constructor(private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer,
              private plotService: WebsiteGraphicsService,
              private gallery: Gallery) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.pipe(debounceTime(5000)).subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
        this.comparisonModel = comparison;
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
    this.comparisonService.getMetrics4Comparison(params).subscribe(
      response => {
      if (response && response.length > 1) {
        response.forEach(metric => {
          this.comparisonMetrics.push(
            new MetricsComparisonDto(metric.metric_query_name, metric.metric_pretty_name));
        });
        this.selectedMetric = this.comparisonMetrics[0];
        this.getComparisonPlots(this.selectedMetric.metric_query_name, comparisonModel);
      } else {
        this.metricsErrorMessage = response[0].message; // this message can be shown somewhere so users know what is wrong
      }
    });
  }

  showGallery(index: number = 0, imagesListObject): void {
    const imagesList = [];
    imagesListObject.forEach(image => {
      imagesList.push({path: this.plotService.plotPrefix + image.plot});
    });
    const prop: any = {};
    prop.component = CarouselComponent;
    prop.images = imagesList;
    prop.index = index;
    prop.arrows = imagesList.length > 1;
    this.gallery.load(prop);
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
    this.metricPlots$ = this.comparisonService.getComparisonPlots(parameters);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

  onMetricChange(): void{
    this.getComparisonPlots(this.selectedMetric.metric_query_name, this.comparisonModel);
  }

  downloadResultFiles(): void {
    // download all the shown images as .png
  }

}

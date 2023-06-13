import {Component, Input, OnInit} from '@angular/core';
import {Observable, of} from 'rxjs';
import {MetricsPlotsDto} from '../../../core/services/validation-run/metrics-plots.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {map} from 'rxjs/operators';
import {PlotDto} from '../../../core/services/global/plot.dto';
import {SafeUrl} from '@angular/platform-browser';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';

@Component({
  selector: 'qa-result-files',
  templateUrl: './result-files.component.html',
  styleUrls: ['./result-files.component.scss']
})
export class ResultFilesComponent implements OnInit {
  @Input() validation: ValidationrunDto;
  faIcons = {faFileDownload: fas.faFileDownload};

  updatedMetrics$: Observable<any>;
  selectedMetrics: MetricsPlotsDto;
  metricIndx = 0;
  selectedBoxplot: any;
  boxplotIndx = 0;
  displayOverviewGallery: boolean;
  displayBoxplotGallery: boolean;

  activeOverviewIndex = 0;
  activeBoxplotIndex = 0;

  constructor(private validationService: ValidationrunService,
              public plotService: WebsiteGraphicsService,
              public globals: GlobalParamsService) {
  }

  ngOnInit(): void {
    this.updateMetricsWithPlots();
    this.updatedMetrics$.subscribe(metrics => {
      this.selectedMetrics = metrics[0];
      this.selectedBoxplot = metrics[0].boxplot_dicts[0];
    });
  }

  private updateMetricsWithPlots(): void {
    const params = new HttpParams().set('validationId', this.validation.id);
    this.updatedMetrics$ = this.validationService.getMetricsAndPlotsNames(params).pipe(
      map((metrics) =>
        metrics.map(
          metric =>
            ({
              ...metric,
              boxplotFiles: this.getPlots(metric.boxplot_dicts.map(boxplotFile => boxplotFile.file)),
              overviewFiles: this.getPlots(metric.overview_files),
            })
        )
      )
    );
  }

  onMetricChange(option): void {
    this.metricIndx = this.selectedMetrics.ind;
    // resetting boxplot index
    this.boxplotIndx = 0;
  }

  onBoxPlotChange(event): void{
    this.boxplotIndx = this.selectedBoxplot.ind;
}

  showGallery(index: number = 0, plotType: string): void {
    if (plotType === 'overview'){
      this.activeOverviewIndex = index;
      this.displayOverviewGallery = true;
    } else {
      this.activeBoxplotIndex = index;
      this.displayBoxplotGallery = true;
    }
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    this.validationService.downloadResultFile(validationId, fileType, fileName);
  }

  getPlots(files: any): Observable<PlotDto[]> {
    let params = new HttpParams();
    // handling an empty list added
    if (files.length === 0 || files[0].length === 0){
      return of([]);
    }

    files.forEach(file => {
      params = params.append('file', file);
    });
    return this.plotService.getPlots(params);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

}

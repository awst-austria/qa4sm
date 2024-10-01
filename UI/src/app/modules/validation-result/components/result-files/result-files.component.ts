import {Component, Input, OnInit, signal, WritableSignal} from '@angular/core';
import {EMPTY, Observable, of, tap} from 'rxjs';
import {MetricsPlotsDto} from '../../../core/services/validation-run/metrics-plots.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {catchError, map} from 'rxjs/operators';
import {PlotDto} from '../../../core/services/global/plot.dto';
import {SafeUrl} from '@angular/platform-browser';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {ToastService} from '../../../core/services/toast/toast.service';

@Component({
  selector: 'qa-result-files',
  templateUrl: './result-files.component.html',
  styleUrls: ['./result-files.component.scss']
})
export class ResultFilesComponent implements OnInit {
  @Input() validation: ValidationrunDto;
  faIcons = {faFileDownload: fas.faFileDownload};

  updatedMetrics$: Observable<MetricsPlotsDto[]>;

  boxplotIndx = 0;
  displayOverviewGallery: boolean;
  displayBoxplotGallery: boolean;
  displayAdditionalPlotGallery: boolean;

  activeOverviewIndex = 0;
  activeBoxplotIndex = 0;
  activeAdditionalPlotIndex = 0;

  selectedMetric: WritableSignal<MetricsPlotsDto> = signal({} as MetricsPlotsDto);

  fileError = signal(false);
  dataFetchError = signal(false);

  constructor(private validationService: ValidationrunService,
              public plotService: WebsiteGraphicsService,
              public globals: GlobalParamsService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.updateMetricsWithPlots();
    console.log(this.validation)
  }

  private updateMetricsWithPlots(): void {
    const params = new HttpParams().set('validationId', this.validation.id);

    this.updatedMetrics$ = this.validationService.getMetricsAndPlotsNames(params)
      .pipe(
        tap((metric) => {
          console.log(metric)
        }),
        map((metrics) =>
          metrics.map(
            metric =>
              ({
                ...metric,
                boxplotFiles: this.getPlots(metric.boxplot_dicts.map(boxplotFile => boxplotFile.file)),
                overviewFiles: this.getPlots(metric.overview_files),
                comparisonFile: metric.comparison_boxplot.length !== 0 ?  this.getPlots(metric.comparison_boxplot) : of(null)
              })
          )
        ),
        tap(data => {
          this.selectedMetric.set(data[0]);
        }),
        catchError((error: CustomHttpError) => {
          this.dataFetchError.set(true);
          this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message);
          return of([] as MetricsPlotsDto[])
        })
      );
  }

  onMetricChange(option): void {
    this.selectedMetric.set(option.value);
    // resetting boxplot index
    this.boxplotIndx = 0;
  }

  onBoxPlotChange(event): void {
    this.boxplotIndx = event.value.ind;
  }

  showGallery(index: number = 0, plotType: string): void {
    if (plotType === 'overview') {
      this.activeOverviewIndex = index;
      this.displayOverviewGallery = true;
    } else if (plotType === 'boxplot') {
      this.activeBoxplotIndex = index;
      this.displayBoxplotGallery = true;
    } else {
      this.displayAdditionalPlotGallery = true;
      this.activeAdditionalPlotIndex = index;
    }
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    this.validationService.downloadResultFile(validationId, fileType, fileName);
  }

  getPlots(files: any): Observable<PlotDto[]> {
    let params = new HttpParams();
    // handling an empty list added
    if (files.length === 0 || files[0].length === 0) {
      return of([]);
    }

    files.forEach(file => {
      params = params.append('file', file);
    });

    return this.plotService.getPlots(params).pipe(
      catchError((error: CustomHttpError) => {
        this.fileError.set(true);
        this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
        return EMPTY;
      })
    );
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

}

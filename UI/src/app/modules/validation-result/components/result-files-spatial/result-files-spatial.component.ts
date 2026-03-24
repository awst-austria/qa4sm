import { CommonModule } from '@angular/common';
import { HttpParams } from '@angular/common/http';
import { Component, Input, OnInit, signal, WritableSignal } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { PanelModule } from 'primeng/panel';
import { SelectModule } from 'primeng/select';
import { GalleriaModule } from 'primeng/galleria';
import { FormsModule } from '@angular/forms';
import { Observable, of, EMPTY } from 'rxjs';
import { map, tap, catchError } from 'rxjs/operators';
import { AsyncPipe } from '@angular/common';
import { ValidationrunDto } from 'src/app/modules/core/services/validation-run/validationrun.dto';
import { ValidationrunService } from 'src/app/modules/core/services/validation-run/validationrun.service';
import { WebsiteGraphicsService } from 'src/app/modules/core/services/global/website-graphics.service';
import { MetricsPlotsDto } from 'src/app/modules/core/services/validation-run/metrics-plots.dto';
import { PlotDto } from 'src/app/modules/core/services/global/plot.dto';
import { SafeUrl } from '@angular/platform-browser';
import { GlobalParamsService } from 'src/app/modules/core/services/global/global-params.service';
import { FloatLabelModule } from 'primeng/floatlabel';
import { Tooltip } from 'primeng/tooltip';

@Component({
  selector: 'qa-result-files-spatial',
  standalone: true,
  imports: [CommonModule, AsyncPipe, FormsModule, PanelModule, ButtonModule, SelectModule, GalleriaModule, FloatLabelModule, Tooltip],
  templateUrl: './result-files-spatial.component.html',
  styleUrl: './result-files-spatial.component.scss',
})
export class ResultFilesSpatialComponent implements OnInit {
  @Input() validation: ValidationrunDto;

  updatedMetrics$: Observable<MetricsPlotsDto[]>;
  selectedMetric: WritableSignal<MetricsPlotsDto> = signal({} as MetricsPlotsDto);

  fileError = signal(false);
  dataFetchError = signal(false);

  displayOverviewGallery = false;
  displayBoxplotGallery = false;
  displayTsplotGallery = false;
  activeTsplotIndex = 0;
  activeOverviewIndex = 0;
  activeBoxplotIndex = 0;
  boxplotIndx = 0;

  constructor(
    private validationService: ValidationrunService,
    public plotService: WebsiteGraphicsService,
    public globals: GlobalParamsService,
  ) {}

  ngOnInit(): void {
    this.loadSpatialData();
  }

  private loadSpatialData(): void {
    const params = new HttpParams().set('validationId', this.validation.id);

    this.updatedMetrics$ = this.validationService.getMetricsAndPlotsNamesSpatial(params).pipe(
    map(metrics => metrics.map(metric => ({
      ...metric,
      boxplotFiles: this.getPlots(
        metric.boxplot_dicts.map(b => b.file).filter(f => f && f.length > 0)
      ),
      overviewFiles: this.getPlots(
        metric.overview_files.filter(f => f && f.length > 0)
      ),
      tsplotFiles: this.getPlots(                          
        (metric.tsplot_file || []).filter(f => f && f.length > 0)
      ),
      comparisonFile: of(null)
    }))),
    tap(data => {
      if (data.length > 0) this.selectedMetric.set(data[0]);
    }),
    catchError(() => {
      this.dataFetchError.set(true);
      return of([] as MetricsPlotsDto[]);
    })
  );
  }

  getPlots(files: string[]): Observable<PlotDto[]> {
    const validFiles = files.filter(f => f && f.length > 0);  // ← фильтруем пустые
    if (!validFiles || validFiles.length === 0) return of([]);
    let params = new HttpParams();
    validFiles.forEach(f => params = params.append('file', f));
    return this.plotService.getPlots(params).pipe(
      catchError(() => {
        this.fileError.set(true);
        return EMPTY;
      })
    );
  }

  onMetricChange(option: any): void {
    this.selectedMetric.set(option.value);
    this.boxplotIndx = 0;
  }

  showGallery(index: number, type: string): void {
    if (type === 'overview') {
      this.activeOverviewIndex = index;
      this.displayOverviewGallery = true;
    } else if (type === 'boxplot') {
      this.activeBoxplotIndex = index;
      this.displayBoxplotGallery = true;
    } else if (type === 'tsplot') {
      this.activeTsplotIndex = index;
      this.displayTsplotGallery = true;
    }
  }

  sanitizePlotUrl(plot: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plot);
  }

  downloadSpatialNetCDF(): void {
    this.validationService.downloadSpatialResultFile(this.validation.id, 'netCDF', `${this.validation.id}_spatial.nc`);
  }

  downloadSpatialGraphics(): void {
    this.validationService.downloadSpatialResultFile(this.validation.id, 'graphics', `${this.validation.id}_spatial_graphs.zip`);
  }

}
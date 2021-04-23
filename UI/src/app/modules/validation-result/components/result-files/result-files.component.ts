import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {MetricsPlotsDto} from '../../../core/services/validation-run/metrics-plots.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {Gallery} from 'angular-gallery';
import {CarouselComponent} from 'angular-gallery/lib/carousel.component.d';
import {fas} from '@fortawesome/free-solid-svg-icons';
import {map} from 'rxjs/operators';
import {PlotDto} from '../../../core/services/global/plot.dto';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';

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
  indx = 0;
  plotPrefix = 'data:image/png;base64,';

  constructor(private validationService: ValidationrunService,
              private plotService: WebsiteGraphicsService,
              private gallery: Gallery,
              private domSanitizer: DomSanitizer) {
  }

  ngOnInit(): void {
    this.updateMetricsWithPlots();
  }

  private updateMetricsWithPlots(): void {
    const params = new HttpParams().set('validationId', this.validation.id);
    this.updatedMetrics$ = this.validationService.getMetricsAndPlotsNames(params).pipe(
      map((metrics) =>
        metrics.map(
          metric =>
            ({
              ...metric,
              boxplotFile: this.getPlots([metric.boxplot_file]),
              overviewFiles: this.getPlots(metric.overview_files)
            })
        )
      )
    );
  }

  onMetricChange(): void {
    this.indx = this.selectedMetrics.ind;
  }

  showGallery(index: number = 0, imagesListObject): void {
    const imagesList = [];
    imagesListObject.forEach(image => {
      imagesList.push({path: this.plotPrefix + image.plot_name});
    });
    const prop: any = {};
    prop.component = CarouselComponent;
    prop.images = imagesList;
    prop.index = index;
    prop.arrows = imagesList.length > 1;
    this.gallery.load(prop);
  }

  downloadResultFile(validationId: string, fileType: string, fileName: string): void {
    this.validationService.downloadResultFile(validationId, fileType, fileName);
  }

  getPlots(files: any): Observable<PlotDto[]> {
    let params = new HttpParams();
    files.forEach(file => {
      params = params.append('file', file);
    });
    return this.plotService.getPlots(params);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.domSanitizer.bypassSecurityTrustUrl(this.plotPrefix + plotBase64);
  }


}

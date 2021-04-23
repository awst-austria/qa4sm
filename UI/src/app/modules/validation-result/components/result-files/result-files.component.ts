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

@Component({
  selector: 'qa-result-files',
  templateUrl: './result-files.component.html',
  styleUrls: ['./result-files.component.scss']
})
export class ResultFilesComponent implements OnInit {
  @Input() validation: ValidationrunDto;
  faIcons = {faFileDownload: fas.faFileDownload};
  selectedMetrics: MetricsPlotsDto;
  overviewPlotsSrc: string[] = [];
  numOfOverviewPlots: number;


  updatedMetrics$: Observable<any>;
  indx = 0;
  plotPrefix = 'data:image/png;base64,';

  constructor(private validationService: ValidationrunService,
              private plotService: WebsiteGraphicsService,
              private gallery: Gallery) {
  }


  ngOnInit(): void {
    this.updateMetricsWithPlots();
    this.getPreliminaryOverviewFiles();
  }

  private updateMetricsWithPlots(): void {
    const params = new HttpParams().set('validationId', this.validation.id);
    this.updatedMetrics$ = this.validationService.getMetricsAndPlotsNames(params).pipe(
      map((metrics) =>
        metrics.map(
          metric =>
            ({
              ...metric,
              boxplotFile: this.getFile(metric.boxplot_file),
              overviewFiles: metric.overview_files.map(file => this.getFile(file))
            })
        )
      )
    );
  }

  getPreliminaryOverviewFiles(): void {
    this.updatedMetrics$.subscribe(data => {
      this.getOverviewPlots(data[0].overview_files);
      this.numOfOverviewPlots = data[0].overview_files.length;
    });
  }

  onMetricChange(): void {
    this.indx = this.selectedMetrics.ind;
    this.getOverviewPlots(this.selectedMetrics.overview_files);
    this.numOfOverviewPlots = this.selectedMetrics.overview_files.length;
  }

  getFile(fileToGet: string): Observable<string> {
    const params = new HttpParams().set('file', fileToGet);
    return this.plotService.getPlot(params);
  }

  getOverviewPlots(filesToGet: any): void {
    this.overviewPlotsSrc = [];
    filesToGet.forEach(file => {
      const params = new HttpParams().set('file', file);
      this.plotService.getPlot(params).subscribe(data => {
        this.overviewPlotsSrc.push('data:image/png;base64,' + data);
      });
    });
  }

  showBoxplot(boxplotPath: string): void {
    const plot = {
      images: [
        {path: boxplotPath}
      ],
      arrows: false
    };
    this.gallery.load(plot);
  }

  showOverviewPlotsGallery(index: number = 0): void {
    const imagesList = [];
    this.overviewPlotsSrc.forEach(plot => {
      imagesList.push({path: plot});
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

}

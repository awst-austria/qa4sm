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

@Component({
  selector: 'qa-result-files',
  templateUrl: './result-files.component.html',
  styleUrls: ['./result-files.component.scss']
})
export class ResultFilesComponent implements OnInit {
  @Input() validation: ValidationrunDto;
  faIcons = {faFileDownload: fas.faFileDownload};
  metricsPlotsNames$: Observable<MetricsPlotsDto[]>;
  selectedMetrics: MetricsPlotsDto;
  boxplotSrc: string;
  overviewPlotsSrc: string[] = [];
  numOfOverviewPlots: number;
  plotsSrc: string[] = [];
  filesList: string[] = [];

  constructor(private validationService: ValidationrunService,
              private plotService: WebsiteGraphicsService,
              private gallery: Gallery) {
  }

  ngOnInit(): void {
    this.getMetricsAndPlotsNames();
  }

  getMetricsAndPlotsNames(): void {
    const params = new HttpParams().set('validationId', this.validation.id);
    this.metricsPlotsNames$ = this.validationService.getMetricsAndPlotsNames(params);
    this.validationService.getMetricsAndPlotsNames(params).subscribe(data => {
      // data[0].overview_files.unshift(data[0].boxplot_file);
      // this.getPlots(data[0].overview_files);
      this.getBoxPlot(data[0].boxplot_file);
      this.getOverviewPlots(data[0].overview_files);
      this.numOfOverviewPlots = data[0].overview_files.length;
    });
  }

  onMetricChange(): void {
    this.getBoxPlot(this.selectedMetrics.boxplot_file);
    this.getOverviewPlots(this.selectedMetrics.overview_files);
    this.numOfOverviewPlots = this.selectedMetrics.overview_files.length;
    // console.log(this.selectedMetrics.overview_files, this.selectedMetrics.boxplot_file);
    // this.filesList = [];
    // this.filesList = this.selectedMetrics.overview_files;
    // this.filesList.unshift(this.selectedMetrics.boxplot_file);
    // this.getPlots(this.filesList);
  }

  getBoxPlot(fileToGet: string): void {
    const params = new HttpParams().set('file', fileToGet);
    this.plotService.getPlot(params).subscribe(data => {
      this.boxplotSrc = 'data:image/png;base64,' + data;
    });
  }

  getOverviewPlots(filesToGet: any): void{
    this.overviewPlotsSrc = [];
    filesToGet.forEach(file => {
      const params = new HttpParams().set('file', file);
      this.plotService.getPlot(params).subscribe(data => {
        this.overviewPlotsSrc.push('data:image/png;base64,' + data);
      });
    });
  }

  // getPlots(filesToGet: any): void{
  //   this.plotsSrc = [];
  //   filesToGet.forEach(file => {
  //     const params = new HttpParams().set('file', file);
  //     this.plotService.getPlot(params).subscribe(data => {
  //       this.plotsSrc.push('data:image/png;base64,' + data);
  //     });
  //   });
  // }

  showBoxplot(): void{
    const plot = {
      images: [
        {path: this.boxplotSrc}
      ],
      arrows: false
    };
    this.gallery.load(plot);
  }

  showOverviewPlotsGallery(index: number = 0): void{
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

  downloadResultFile(validationId: string, fileType: string, fileName: string): void{
    this.validationService.downloadResultFile(validationId, fileType, fileName);
  }

}

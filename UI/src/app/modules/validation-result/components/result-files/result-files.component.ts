import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {MetricsPlotsDto} from '../../../core/services/validation-run/metrics-plots.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';

@Component({
  selector: 'qa-result-files',
  templateUrl: './result-files.component.html',
  styleUrls: ['./result-files.component.scss']
})
export class ResultFilesComponent implements OnInit {
  @Input() validation: ValidationrunDto;
  metricsPlotsNames$: Observable<MetricsPlotsDto[]>;
  selectedMetrics: MetricsPlotsDto;
  boxplotSrc: string;
  overviewPlotsSrc: string[] = [];
  numOfOverviewPlots: number;

  constructor(private validationService: ValidationrunService,
              private plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    this.getMetricsAndPlotsNames();
  }

  getMetricsAndPlotsNames(): void {
    const params = new HttpParams().set('validationId', this.validation.id);
    this.metricsPlotsNames$ = this.validationService.getMetricsAndPlotsNames(params);
    this.validationService.getMetricsAndPlotsNames(params).subscribe(data => {
      this.getBoxPlot(data[0].boxplot_file);
      this.getOverviewPlots(data[0].overview_files);
      this.numOfOverviewPlots = data[0].overview_files.length;
    });
  }

  onMetricChange(): void {
    this.getBoxPlot(this.selectedMetrics.boxplot_file);
    this.getOverviewPlots(this.selectedMetrics.overview_files);

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

}

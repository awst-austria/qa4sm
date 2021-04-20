import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {MetricsPlotsDto} from '../../../core/services/validation-run/metrics-plots.dto';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';

@Component({
  selector: 'qa-result-files',
  templateUrl: './result-files.component.html',
  styleUrls: ['./result-files.component.scss']
})
export class ResultFilesComponent implements OnInit {
  @Input() validationId: string;
  metricsPlotsNames$: Observable<MetricsPlotsDto[]>;

  constructor(private validationService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.getMetricsAndPlotsNames();
  }

  getMetricsAndPlotsNames(): void {
    const params = new HttpParams().set('validationId', this.validationId);
    this.metricsPlotsNames$ = this.validationService.getMetricsAndPlotsNames(params);
  }

  onMetricChange(): void {
    console.log('Metric has changed');
  }
}

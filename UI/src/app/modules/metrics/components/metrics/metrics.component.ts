import {Component, Input, OnInit} from '@angular/core';
import {MetricModel} from '../metric/metric-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';

export const TRIPLE_COLLOCATION = 'tcol';
export let METRIC_LIST = {};
METRIC_LIST[TRIPLE_COLLOCATION] = false;

@Component({
  selector: 'qa-metrics',
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss']
})
export class MetricsComponent implements OnInit {
  @Input() validationModel: ValidationModel;
  @Input() metricsList: any;

  tripleCollocationMetrics: MetricModel;

  constructor() {
  }

  ngOnInit(): void {
    this.tripleCollocationMetrics = new MetricModel('Include Triple Collocation Metrics',
      'Triple collocation analysis is only available if 3 or more data sets (including the reference) are selected.',
      this.metricsList.tcol,
      false,
      TRIPLE_COLLOCATION);
    this.validationModel.metrics.push(this.tripleCollocationMetrics);
  }

}

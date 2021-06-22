import {Component, Input, OnInit} from '@angular/core';
import {MetricModel} from '../metric/metric-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';
import {BehaviorSubject} from 'rxjs';

@Component({
  selector: 'qa-metrics',
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss']
})
export class MetricsComponent implements OnInit {
  @Input() validationModel: ValidationModel;

  tripleCollocationMetrics: MetricModel;

  constructor() {
  }

  ngOnInit(): void {
    this.tripleCollocationMetrics = new MetricModel('Include Triple Collocation Metrics', 'Triple collocation analysis is only available if 3 or more data sets (including the reference) are selected.', new BehaviorSubject<boolean>(false), false, 'tcol');
    this.validationModel.metrics.push(this.tripleCollocationMetrics);
  }

}

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
  bootstrapTripleCollocationMetrics: MetricModel;

  constructor() {
  }

  ngOnInit(): void {
    this.tripleCollocationMetrics = new MetricModel('Include Triple Collocation Metrics',
      'Triple collocation analysis is only available if 3 or more data sets (including the reference) are selected.',
      new BehaviorSubject<boolean>(false),
      false,
      'tcol');
    this.validationModel.metrics.push(this.tripleCollocationMetrics);

    this.bootstrapTripleCollocationMetrics = new MetricModel(
      'Bootstrap Triple Collocation metric confidence intervals (Warning: very slow)',
      'Calculates confidence intervals via bootstrapping with 1000 repetitions. This can significantly impact performance, typically increases runtime by a factor of 5.',
      new BehaviorSubject<boolean>(false), false, 'bootstrap_tcol_cis');
    this.validationModel.metrics.push(this.bootstrapTripleCollocationMetrics);
  }

  switchOffBootstrap(): void {
    if (!this.tripleCollocationMetrics.value$.getValue()) {
      this.bootstrapTripleCollocationMetrics.value$.next(false);
    }
  }

  checkIfDisabled(metricName: string): boolean {
    let condition = true;
    const conditionTcol = this.validationModel.datasetConfigurations.length < 2;
    const conditionBtcol = conditionTcol ||
      !(this.validationModel.datasetConfigurations.length  > 1 && this. tripleCollocationMetrics.value$.getValue());

    if (conditionTcol) {
      this.tripleCollocationMetrics.value$.next(false);
      this.bootstrapTripleCollocationMetrics.value$.next(false);
    } else {
      if (metricName === 'tcol'){
        condition = conditionTcol;
      } else if (metricName === 'btcol') {
        condition = conditionBtcol;
      }
    }
    return condition;
  }

}

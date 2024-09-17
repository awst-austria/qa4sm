import {Component, model, OnChanges, OnInit, signal, SimpleChanges} from '@angular/core';
import {MetricModel} from '../metric/metric-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';

@Component({
  selector: 'qa-metrics',
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss']
})
export class MetricsComponent implements OnInit, OnChanges {
  validationModel = model<ValidationModel|null>(null);
  // @Input() validationModel: ValidationModel;

  tripleCollocationMetrics: MetricModel;
  bootstrapTripleCollocationMetrics: MetricModel;
  stabilityMetrics: MetricModel;

  constructor() {
  }

  ngOnInit(): void {
    this.tripleCollocationMetrics = new MetricModel('Include Triple Collocation Metrics',
      'Triple collocation analysis is only available if 3 or more data sets (including the reference) are selected.',
      signal(false),
      false,
      'tcol');

    this.bootstrapTripleCollocationMetrics = new MetricModel(
      'Bootstrap Triple Collocation metric confidence intervals (Warning: very slow)',
      'Calculates confidence intervals via bootstrapping with 1000 repetitions. ' +
      'This can significantly impact performance, typically increases runtime by a factor of 5.',
      signal(false),
      false,
      'bootstrap_tcol_cis',
      );

    this.stabilityMetrics = new MetricModel(
      'Include Stability Metrics',
      'Here we will explain what stability metrics are',
      signal(false),
      false,
      'stability_metrics'
    )

    this.validationModel.update(model => {
      model.metrics.push(this.tripleCollocationMetrics, this.bootstrapTripleCollocationMetrics, this.stabilityMetrics)
      return model
    })
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log(changes)
  }

  switchOffBootstrap = () => {
    if (this.tripleCollocationMetrics.value()) {
      this.bootstrapTripleCollocationMetrics.value.set(false);
    }
  }

  checkIfDisabled(metricName: string): boolean {
    let condition = true;
    const conditionTcol = this.validationModel().datasetConfigurations.length < 3;
    const conditionBtcol = conditionTcol ||
      !(this.validationModel().datasetConfigurations.length  > 2 && this. tripleCollocationMetrics.value());

    if (conditionTcol) {
      // this.tripleCollocationMetrics.value.set(false);
      // this.bootstrapTripleCollocationMetrics.value.set(false);
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

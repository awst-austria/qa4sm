import {Component, model, OnInit} from '@angular/core';
import {MetricModel} from '../metric/metric-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';

@Component({
  selector: 'qa-metrics',
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss']
})
export class MetricsComponent implements OnInit {
  validationModel = model<ValidationModel>();

  tripleCollocationMetrics: MetricModel;
  bootstrapTripleCollocationMetrics: MetricModel;
  stabilityMetrics: MetricModel;

  constructor() {
  }

  ngOnInit(): void {
    this.tripleCollocationMetrics = new MetricModel(
      'tcol',
      'Include Triple Collocation Metrics',
      'Triple collocation analysis is only available if 3 or more data sets (including the reference) are selected.',
      false,
      this.tripleCollocationDisabled.bind(this),
      this.onTripleCollocationMetricsChanged.bind(this));

    this.bootstrapTripleCollocationMetrics = new MetricModel(
      'bootstrap_tcol_cis',
      'Bootstrap Triple Collocation metric confidence intervals (Warning: very slow)',
      'Calculates confidence intervals via bootstrapping with 1000 repetitions. ' +
      'This can significantly impact performance, typically increases runtime by a factor of 5.',
      false,
      this.bootstrapingDisabled.bind(this),
    );

    this.stabilityMetrics = new MetricModel(
      'stability_metrics',
      'Include Stability Metrics',
      'Here we will explain what stability metrics are',
      false,
      this.stabilityMetricsDisabled.bind(this),
    )


    this.validationModel.update(model => {
      model.metrics.push(this.tripleCollocationMetrics, this.bootstrapTripleCollocationMetrics, this.stabilityMetrics)
      return model
    });
  }

  onTripleCollocationMetricsChanged(newValue: boolean): void {
    if (!newValue) {
      this.bootstrapTripleCollocationMetrics.value = false;
    } else {
    }
  }

  tripleCollocationDisabled(): boolean {
    return this.validationModel().datasetConfigurations.length < 3;
  }

  bootstrapingDisabled(): boolean {
    return this.validationModel().datasetConfigurations.length < 3 || !this.tripleCollocationMetrics.value
  }

  stabilityMetricsDisabled(): boolean {
    return this.validationModel().intraAnnualMetrics.intra_annual_metrics;
  }

  checkIfDisabled(metric: MetricModel): boolean {
    return metric.triggerDisabledCheck();
  }


}

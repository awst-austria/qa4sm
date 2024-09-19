import {Component, model, OnInit} from '@angular/core';
import {MetricModel} from '../metric/metric-model';
import {ValidationModel} from '../../../../pages/validate/validation-model';

@Component({
  selector: 'qa-metrics',
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss']
})
export class MetricsComponent implements OnInit {
  // If a new metric that requires only a checkbox should be added, follow the comments below.
  validationModel = model<ValidationModel>(); // don't touch this one.

  tripleCollocationMetrics: MetricModel;
  bootstrapTripleCollocationMetrics: MetricModel;
  stabilityMetrics: MetricModel;
  // ad a metric instance


  constructor() {
  }

  ngOnInit(): void {
    this.tripleCollocationMetrics = new MetricModel(
      'tcol',
      'Include Triple Collocation Metrics',
      'Triple collocation analysis is only available if 3 or more data sets (including the reference) are selected.',
      false,
      true,
      this.tripleCollocationDisabled.bind(this),
      this.onTripleCollocationMetricsChanged.bind(this));

    this.bootstrapTripleCollocationMetrics = new MetricModel(
      'bootstrap_tcol_cis',
      'Bootstrap Triple Collocation metric confidence intervals (Warning: very slow)',
      'Calculates confidence intervals via bootstrapping with 1000 repetitions. ' +
      'This can significantly impact performance, typically increases runtime by a factor of 5.',
      false,
      true,
      this.bootstrapingDisabled.bind(this),
    );

    this.stabilityMetrics = new MetricModel(
      'stability_metrics',
      'Include Stability Metrics',
      'Here we will explain what stability metrics are',
      false,
      true,
      this.stabilityMetricsDisabled.bind(this),
    )

    // define the metric according to the model (like above) and then push it to the validation model (like below).

    this.validationModel.update(model => {
      model.metrics.push(this.tripleCollocationMetrics, this.bootstrapTripleCollocationMetrics, this.stabilityMetrics)
      return model
    });
  }

  // define a function that disables the metric (remember about enabling it as well).
  // If the metric should be never disabled, just pass '() => false' as isDisabled callback

  tripleCollocationDisabled(): boolean {
    return this.validationModel().datasetConfigurations.length < 3;
  }

  bootstrapingDisabled(): boolean {
    return this.validationModel().datasetConfigurations.length < 3 || !this.tripleCollocationMetrics.value
  }

  stabilityMetricsDisabled(): boolean {
    return this.validationModel().intraAnnualMetrics.intra_annual_metrics;
  }

  // If something else should happen, when the metric is checked, add a proper function here

  onTripleCollocationMetricsChanged(newValue: boolean): void {
    if (!newValue) {
      this.bootstrapTripleCollocationMetrics.value = false;
    }
  }

  // this one is triggered to call a function assigned to the particular metric to check if it should be disabled
  checkIfDisabled(metric: MetricModel): boolean {
    return metric.triggerDisabledCheck(metric.switchOffIfDisabled);
  }


}

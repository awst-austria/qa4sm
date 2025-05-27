import { Component, model, OnInit } from '@angular/core';
import { MetricModel } from '../metric/metric-model';
import { ValidationModel } from '../../../../pages/validate/validation-model';

/**
If a new metric that requires only a checkbox should be added, follow the comments below.
If you add a metric properly, there is no need to update validate page. Other updates that are required:
ValidationRun model, validation_config_view (api view) and validation-summary component to display information if the
metric has been included or not.

There might be also other updates required, like, including new plots or so, but that's already metric specific
information.
 */

@Component({
  selector: 'qa-metrics',
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss'],
  standalone: false,
})
export class MetricsComponent implements OnInit {

  validationModel = model<ValidationModel>(); // don't touch this one.

  tripleCollocationMetrics: MetricModel;
  bootstrapTripleCollocationMetrics: MetricModel;
  stabilityMetrics: MetricModel;
  // ad a metric instance


  constructor() {
  }

  ngOnInit(): void {
    // define the metric according to the model - the first entry, i.e. the name attribute, should be the same as the
    // respective entry in the ValidationRun model, this way there will be no need to update serializer in the api views
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
      'Slopes are derived from annual R, uRMSD, and BIAS values to capture performance trends over time. Additionally, all metrics are calculated separately for each year in the validation period.',
      false,
      true,
      this.stabilityMetricsDisabled.bind(this),
    )

    // Push it to the validation model.
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

  intraAnnulMetricDisabled(): boolean{
    return this.stabilityMetrics.value;
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

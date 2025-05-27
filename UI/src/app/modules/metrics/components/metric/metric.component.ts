import { Component, input, model } from '@angular/core';
import { MetricModel } from './metric-model';

@Component({
  selector: 'qa-metric',
  templateUrl: './metric.component.html',
  styleUrls: ['./metric.component.scss'],
  standalone: false,
})
export class MetricComponent {

  metricModel = model<MetricModel>(null);
  // @Input() metricModel: MetricModel;
  disabled = input<boolean | null>(null);

  constructor() {
  }

  onValueChange(newValue: boolean): void {
    // Update the signal's value
      this.metricModel().value = newValue;

      // Trigger the onChange callback if it exists
      this.metricModel().triggerOnChange(newValue);

  }
}

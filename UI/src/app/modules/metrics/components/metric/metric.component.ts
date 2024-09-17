import {Component, Input, model} from '@angular/core';
import {MetricModel} from './metric-model';

@Component({
  selector: 'qa-metric',
  templateUrl: './metric.component.html',
  styleUrls: ['./metric.component.scss']
})
export class MetricComponent {

  // @Input() metricModel: MetricModel;
  metricModel = model<MetricModel>(null);
  @Input() disabled: boolean = false;

  constructor() {
  }

}

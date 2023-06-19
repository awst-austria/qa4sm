import {Component, Input} from '@angular/core';
import {MetricModel} from './metric-model';

@Component({
  selector: 'qa-metric',
  templateUrl: './metric.component.html',
  styleUrls: ['./metric.component.scss']
})
export class MetricComponent {

  @Input() metricModel: MetricModel;
  @Input() disabled: boolean = false;

  constructor() {
  }

}

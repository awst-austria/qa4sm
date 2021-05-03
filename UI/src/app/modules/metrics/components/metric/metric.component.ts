import {Component, Input, OnInit} from '@angular/core';
import {MetricModel} from './metric-model';

@Component({
  selector: 'qa-metric',
  templateUrl: './metric.component.html',
  styleUrls: ['./metric.component.scss']
})
export class MetricComponent implements OnInit {

  @Input() metricModel: MetricModel;
  @Input() disabled: boolean = false;

  constructor() {
  }

  ngOnInit(): void {
  }

}

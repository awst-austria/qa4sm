import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MetricComponent} from './components/metric/metric.component';
import {MetricsComponent} from './components/metrics/metrics.component';
import {CheckboxModule} from 'primeng/checkbox';
import {TooltipModule} from 'primeng/tooltip';
import {PanelModule} from 'primeng/panel';
import {FormsModule} from '@angular/forms';


@NgModule({
  declarations: [MetricComponent, MetricsComponent],
  exports: [
    MetricsComponent
  ],
  imports: [
    CommonModule,
    CheckboxModule,
    TooltipModule,
    PanelModule,
    FormsModule
  ]
})
export class MetricsModule { }

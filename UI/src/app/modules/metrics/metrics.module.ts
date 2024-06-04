import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MetricComponent} from './components/metric/metric.component';
import {MetricsComponent} from './components/metrics/metrics.component';
import {CheckboxModule} from 'primeng/checkbox';
import {TooltipModule} from 'primeng/tooltip';
import {PanelModule} from 'primeng/panel';
import {FormsModule} from '@angular/forms';
import {DropdownModule} from "primeng/dropdown";
import {SeasonalMetricsComponent} from './components/seasonal-metrics/seasonal-metrics.component';
import {InputNumberModule} from "primeng/inputnumber";


@NgModule({
  declarations: [MetricComponent, MetricsComponent, SeasonalMetricsComponent],
  exports: [
    MetricsComponent
  ],
  imports: [
    CommonModule,
    CheckboxModule,
    TooltipModule,
    PanelModule,
    FormsModule,
    DropdownModule,
    InputNumberModule
  ]
})
export class MetricsModule { }

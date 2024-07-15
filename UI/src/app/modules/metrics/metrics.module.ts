import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MetricComponent} from './components/metric/metric.component';
import {MetricsComponent} from './components/metrics/metrics.component';
import {CheckboxModule} from 'primeng/checkbox';
import {TooltipModule} from 'primeng/tooltip';
import {PanelModule} from 'primeng/panel';
import {FormsModule} from '@angular/forms';
import {DropdownModule} from "primeng/dropdown";
import {InputNumberModule} from "primeng/inputnumber";
import {IntraAnnualMetricsComponent} from "./components/intra-annual-metrics/intra-annual-metrics.component";


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
    FormsModule,
    DropdownModule,
    InputNumberModule,
    IntraAnnualMetricsComponent
  ]
})
export class MetricsModule { }

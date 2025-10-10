import {NgModule} from '@angular/core';
import {MetricComponent} from './components/metric/metric.component';
import {MetricsComponent} from './components/metrics/metrics.component';
import {IntraAnnualMetricsComponent} from "./components/intra-annual-metrics/intra-annual-metrics.component";
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [MetricComponent, MetricsComponent],
  exports: [
    MetricsComponent
  ],
  imports: [
    SharedPrimeNgModule,
    IntraAnnualMetricsComponent
  ]
})
export class MetricsModule { }

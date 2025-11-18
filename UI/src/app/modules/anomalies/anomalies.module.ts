import {NgModule} from '@angular/core';
import {AnomClimatologyComponent} from './components/anom-climatology/anom-climatology.component';
import {AnomaliesComponent} from './components/anomalies/anomalies.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [AnomClimatologyComponent, AnomaliesComponent],
  exports: [
    AnomaliesComponent
  ],
  imports: [
    SharedPrimeNgModule
  ]
})
export class AnomaliesModule {
}

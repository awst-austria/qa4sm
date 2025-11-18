import {NgModule} from '@angular/core';
import {ScalingComponent} from './components/scaling/scaling.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';


@NgModule({
  declarations: [ScalingComponent],
  exports: [
    ScalingComponent
  ],
  imports: [
    SharedPrimeNgModule
  ]
})
export class ScalingModule {
}

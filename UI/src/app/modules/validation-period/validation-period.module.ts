import { NgModule } from '@angular/core';
import { ValidationPeriodComponent } from './components/validation-period/validation-period.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';



@NgModule({
  declarations: [ValidationPeriodComponent],
  exports: [
    ValidationPeriodComponent
  ],
  imports: [
    SharedPrimeNgModule
  ]
})
export class ValidationPeriodModule { }

import { NgModule } from '@angular/core';
import { SpatialSubsetComponent } from './components/spatial-subset/spatial-subset.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [SpatialSubsetComponent],
  exports: [
    SpatialSubsetComponent
  ],
  imports: [
    SharedPrimeNgModule
  ]
})
export class SpatialSubsetModule { }

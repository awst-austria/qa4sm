import {NgModule} from '@angular/core';
import {DatasetComponent} from './components/dataset/dataset.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [DatasetComponent],
    exports: [
        DatasetComponent,
    ],
  imports: [
    SharedPrimeNgModule
  ]
})
export class DatasetModule {
}

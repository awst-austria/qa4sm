import {NgModule} from '@angular/core';
import {DatasetComponent} from './components/dataset/dataset.component';
import {MergeLayersComponent} from './components/merge-layers/merge-layers.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [DatasetComponent, MergeLayersComponent],
    exports: [
        DatasetComponent,
        MergeLayersComponent,
    ],
  imports: [
    SharedPrimeNgModule
  ]
})
export class DatasetModule {
}

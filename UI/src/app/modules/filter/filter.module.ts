import {NgModule} from '@angular/core';
import {BasicFilterComponent} from './components/basic-filter/basic-filter.component';
import {IsmnNetworkFilterComponent} from './components/ismn-network-filter/ismn-network-filter.component';
import {TreeModule} from 'primeng/tree';
import {IsmnDepthFilterComponent} from './components/ismn-depth-filter/ismn-depth-filter.component';
import { ThresholdFilterComponent } from './components/threshold-filter/threshold-filter.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [BasicFilterComponent, IsmnNetworkFilterComponent, IsmnDepthFilterComponent, ThresholdFilterComponent],
    exports: [
        BasicFilterComponent,
        IsmnNetworkFilterComponent,
        IsmnDepthFilterComponent,
        ThresholdFilterComponent
    ],
    imports: [
        SharedPrimeNgModule,
        TreeModule,
    ]
})
export class FilterModule {
}

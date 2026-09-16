import {NgModule} from '@angular/core';
import {BasicFilterComponent} from './components/basic-filter/basic-filter.component';
import {IsmnNetworkFilterComponent} from './components/ismn-network-filter/ismn-network-filter.component';
import {TreeModule} from 'primeng/tree';
import {IsmnDepthFilterComponent} from './components/ismn-depth-filter/ismn-depth-filter.component';
import {IsmnTolerancesFilterComponent} from './components/ismn-tolerances-filter/ismn-tolerances-filter.component';
import {IsmnDepthSettingsComponent} from './components/ismn-depth-settings/ismn-depth-settings.component';
import { ThresholdFilterComponent } from './components/threshold-filter/threshold-filter.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  // IsmnDepthFilterComponent and IsmnTolerancesFilterComponent are superseded
  // on the validate page by IsmnDepthSettingsComponent, which presents both as
  // one panel. They are kept declared, unused, rather than deleted in the same
  // change that introduces their replacement.
  declarations: [BasicFilterComponent, IsmnNetworkFilterComponent, IsmnDepthFilterComponent, IsmnTolerancesFilterComponent, IsmnDepthSettingsComponent, ThresholdFilterComponent],
    exports: [
        BasicFilterComponent,
        IsmnNetworkFilterComponent,
        IsmnDepthFilterComponent,
        IsmnTolerancesFilterComponent,
        IsmnDepthSettingsComponent,
        ThresholdFilterComponent
    ],
    imports: [
        SharedPrimeNgModule,
        TreeModule,
    ]
})
export class FilterModule {
}

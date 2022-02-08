import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CheckboxModule} from 'primeng/checkbox';
import {BasicFilterComponent} from './components/basic-filter/basic-filter.component';
import {FormsModule} from '@angular/forms';
import {IsmnNetworkFilterComponent} from './components/ismn-network-filter/ismn-network-filter.component';
import {ButtonModule} from 'primeng/button';
import {DialogModule} from 'primeng/dialog';
import {TreeModule} from 'primeng/tree';
import {TooltipModule} from 'primeng/tooltip';
import {IsmnDepthFilterComponent} from './components/ismn-depth-filter/ismn-depth-filter.component';
import {InputNumberModule} from 'primeng/inputnumber';


@NgModule({
  declarations: [BasicFilterComponent, IsmnNetworkFilterComponent, IsmnDepthFilterComponent],
  exports: [
    BasicFilterComponent,
    IsmnNetworkFilterComponent,
    IsmnDepthFilterComponent
  ],
    imports: [
        CommonModule,
        CheckboxModule,
        FormsModule,
        ButtonModule,
        DialogModule,
        TreeModule,
        TooltipModule,
        InputNumberModule

    ]
})
export class FilterModule {
}

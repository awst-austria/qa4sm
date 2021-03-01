import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ScalingComponent} from './components/scaling/scaling.component';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';
import {DropdownModule} from 'primeng/dropdown';
import {FormsModule} from '@angular/forms';


@NgModule({
  declarations: [ScalingComponent],
  exports: [
    ScalingComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    TooltipModule,
    DropdownModule,
    FormsModule
  ]
})
export class ScalingModule {
}

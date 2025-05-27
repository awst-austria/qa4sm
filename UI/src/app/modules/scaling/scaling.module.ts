import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ScalingComponent } from './components/scaling/scaling.component';
import { PanelModule } from 'primeng/panel';
import { TooltipModule } from 'primeng/tooltip';
import { FormsModule } from '@angular/forms';
import { Select } from 'primeng/select';


@NgModule({
  declarations: [ScalingComponent],
  exports: [
    ScalingComponent
  ],
    imports: [
        CommonModule,
        PanelModule,
        TooltipModule,
        FormsModule,
        Select
    ]
})
export class ScalingModule {
}

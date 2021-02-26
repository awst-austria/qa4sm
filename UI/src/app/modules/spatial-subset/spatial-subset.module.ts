import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SpatialSubsetComponent } from './components/spatial-subset/spatial-subset.component';
import {PanelModule} from 'primeng/panel';
import {ButtonModule} from 'primeng/button';
import {TooltipModule} from 'primeng/tooltip';
import {InputTextModule} from 'primeng/inputtext';



@NgModule({
  declarations: [SpatialSubsetComponent],
  exports: [
    SpatialSubsetComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    ButtonModule,
    TooltipModule,
    InputTextModule
  ]
})
export class SpatialSubsetModule { }

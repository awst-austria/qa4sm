import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SpatialSubsetComponent } from './components/spatial-subset/spatial-subset.component';
import {PanelModule} from 'primeng/panel';
import {ButtonModule} from 'primeng/button';



@NgModule({
  declarations: [SpatialSubsetComponent],
  exports: [
    SpatialSubsetComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    ButtonModule
  ]
})
export class SpatialSubsetModule { }

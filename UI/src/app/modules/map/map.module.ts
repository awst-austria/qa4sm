import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MapComponent} from './components/map/map.component';
import {MapLegendComponent} from './components/map-legend/map-legend.component';
import {TooltipModule} from 'primeng/tooltip';


@NgModule({
  declarations: [MapComponent, MapLegendComponent],
  exports: [
    MapComponent,
    MapLegendComponent
  ],
  imports: [
    CommonModule,
    TooltipModule
  ]
})
export class MapModule {
}

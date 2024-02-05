import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MapComponent} from './components/map/map.component';
import {MapLegendComponent} from './components/map-legend/map-legend.component';
import {TooltipModule} from 'primeng/tooltip';
import {ScrollPanelModule} from 'primeng/scrollpanel';


@NgModule({
  declarations: [MapComponent, MapLegendComponent],
  exports: [
    MapComponent,
    MapLegendComponent
  ],
    imports: [
        CommonModule,
        TooltipModule,
        ScrollPanelModule
    ]
})
export class MapModule {
}

import {NgModule} from '@angular/core';
import {MapComponent} from './components/map/map.component';
import {MapLegendComponent} from './components/map-legend/map-legend.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [MapComponent, MapLegendComponent],
  exports: [
    MapComponent,
    MapLegendComponent
  ],
    imports: [
        SharedPrimeNgModule
    ]
})
export class MapModule {
}

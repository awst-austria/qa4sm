import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MapComponent} from './components/map/map.component';


@NgModule({
  declarations: [MapComponent],
  exports: [
    MapComponent
  ],
  imports: [
    CommonModule
  ]
})
export class MapModule {
}

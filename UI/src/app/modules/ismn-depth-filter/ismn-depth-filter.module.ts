import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {IsmnDepthFilterComponent} from './ismn-depth-filter/ismn-depth-filter.component';


@NgModule({
  declarations: [IsmnDepthFilterComponent],
  exports: [
    IsmnDepthFilterComponent
  ],
  imports: [
    CommonModule
  ]
})
export class IsmnDepthFilterModule {
}

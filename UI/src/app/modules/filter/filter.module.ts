import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CheckboxModule} from 'primeng/checkbox';
import { BasicFilterComponent } from './components/basic-filter/basic-filter.component';


@NgModule({
  declarations: [BasicFilterComponent],
  exports: [
    BasicFilterComponent
  ],
  imports: [
    CommonModule,
    CheckboxModule

  ]
})
export class FilterModule {
}

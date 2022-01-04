import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CheckboxModule} from 'primeng/checkbox';
import {BasicFilterComponent} from './components/basic-filter/basic-filter.component';
import {FormsModule} from '@angular/forms';
import {TooltipModule} from 'primeng/tooltip';


@NgModule({
  declarations: [BasicFilterComponent],
  exports: [
    BasicFilterComponent
  ],
    imports: [
        CommonModule,
        CheckboxModule,
        FormsModule,
        TooltipModule

    ]
})
export class FilterModule {
}

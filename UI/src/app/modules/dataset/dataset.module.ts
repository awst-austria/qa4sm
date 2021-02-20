import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {DatasetComponent} from './components/dataset/dataset.component';
import {FormsModule} from '@angular/forms';
import {DropdownModule} from 'primeng/dropdown';
import {ButtonModule} from 'primeng/button';

@NgModule({
  declarations: [DatasetComponent],
  exports: [
    DatasetComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    DropdownModule,
    ButtonModule
  ]
})
export class DatasetModule {
}

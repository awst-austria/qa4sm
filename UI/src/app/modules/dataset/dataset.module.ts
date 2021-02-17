import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DatasetComponent } from './components/dataset/dataset.component';
import {DropdownModule} from 'primeng/dropdown';
import {FormsModule} from '@angular/forms';



@NgModule({
  declarations: [DatasetComponent],
  exports: [
    DatasetComponent
  ],
  imports: [
    CommonModule,
    DropdownModule,
    FormsModule
  ]
})
export class DatasetModule { }

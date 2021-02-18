import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DatasetComponent } from './components/dataset/dataset.component';
import {FormsModule} from '@angular/forms';



@NgModule({
  declarations: [DatasetComponent],
  exports: [
    DatasetComponent
  ],
  imports: [
    CommonModule,
    FormsModule
  ]
})
export class DatasetModule { }

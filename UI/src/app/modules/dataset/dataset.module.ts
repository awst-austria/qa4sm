import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DatasetComponent } from './components/dataset/dataset.component';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { Select } from 'primeng/select';

@NgModule({
  declarations: [DatasetComponent],
    exports: [
        DatasetComponent,
    ],
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    Select
  ]
})
export class DatasetModule {
}

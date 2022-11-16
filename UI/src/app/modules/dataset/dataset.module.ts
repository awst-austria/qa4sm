import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {DatasetComponent} from './components/dataset/dataset.component';
import {FormsModule} from '@angular/forms';
import {DropdownModule} from 'primeng/dropdown';
import {ButtonModule} from 'primeng/button';
import {DatasetReferenceComponent} from './components/dataset-reference/dataset-reference.component';

@NgModule({
  declarations: [DatasetComponent, DatasetReferenceComponent],
    exports: [
        DatasetComponent,
        DatasetReferenceComponent
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

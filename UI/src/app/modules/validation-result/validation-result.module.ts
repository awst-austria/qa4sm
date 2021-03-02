import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationrunRowComponent } from './components/validationrun-row/validationrun-row.component';
import {PanelModule} from 'primeng/panel';


@NgModule({
    declarations: [ValidationrunRowComponent],
    exports: [
        ValidationrunRowComponent
    ],
  imports: [
    CommonModule,
    PanelModule,
  ]
})
export class ValidationResultModule { }

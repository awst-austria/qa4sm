import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TemporalMatchingComponent } from './components/temporal-matching/temporal-matching.component';
import { InputNumber } from 'primeng/inputnumber';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [TemporalMatchingComponent],
  exports: [TemporalMatchingComponent],
  imports: [
    CommonModule,
    InputNumber,
    FormsModule
  ]
})
export class TemporalMatchingModule { }

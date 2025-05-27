import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TemporalMatchingComponent } from './components/temporal-matching/temporal-matching.component';


@NgModule({
  declarations: [TemporalMatchingComponent],
  exports: [TemporalMatchingComponent],
  imports: [
    CommonModule
  ]
})
export class TemporalMatchingModule { }

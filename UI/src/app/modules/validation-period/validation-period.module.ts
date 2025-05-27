import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationPeriodComponent } from './components/validation-period/validation-period.component';
import { PanelModule } from 'primeng/panel';
import { TooltipModule } from 'primeng/tooltip';
import { FormsModule } from '@angular/forms';
import { DatePicker } from 'primeng/datepicker';

1;


@NgModule({
  declarations: [ValidationPeriodComponent],
  exports: [
    ValidationPeriodComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    TooltipModule,
    FormsModule,
    DatePicker
  ]
})
export class ValidationPeriodModule { }

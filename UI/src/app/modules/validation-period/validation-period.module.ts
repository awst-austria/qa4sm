import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationPeriodComponent } from './components/validation-period/validation-period.component';
import { PanelModule } from 'primeng/panel';
import { TooltipModule } from 'primeng/tooltip';
import { CalendarModule } from 'primeng/calendar';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [ValidationPeriodComponent],
  exports: [
    ValidationPeriodComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    TooltipModule,
    CalendarModule,
    FormsModule,
    ValidationPeriodComponent
  ]
})
export class ValidationPeriodModule { }

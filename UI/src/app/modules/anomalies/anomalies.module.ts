import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AnomClimatologyComponent} from './components/anom-climatology/anom-climatology.component';
import {AnomaliesComponent} from './components/anomalies/anomalies.component';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';
import {DropdownModule} from 'primeng/dropdown';
import {FormsModule} from '@angular/forms';
import {CalendarModule} from 'primeng/calendar';


@NgModule({
  declarations: [AnomClimatologyComponent, AnomaliesComponent],
  exports: [
    AnomaliesComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    TooltipModule,
    DropdownModule,
    FormsModule,
    CalendarModule
  ]
})
export class AnomaliesModule {
}

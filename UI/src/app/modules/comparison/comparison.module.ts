import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {NgxPaginationModule} from 'ngx-pagination';
import {RouterModule} from '@angular/router';
import {DropdownModule} from 'primeng/dropdown';
import {FormsModule} from '@angular/forms';
import {InputTextModule} from 'primeng/inputtext';
import {ValidationSelectorComponent} from './components/validation-selector/validation-selector.component';
import {PlotsComponent} from './components/plots/plots.component';
import {AccordionModule} from "primeng/accordion";

@NgModule({
    declarations: [ValidationSelectorComponent, PlotsComponent],
    exports: [
        ValidationSelectorComponent, PlotsComponent
    ],
  imports: [
    CommonModule,
    PanelModule,
    TooltipModule,
    FontAwesomeModule,
    NgxPaginationModule,
    RouterModule,
    DropdownModule,
    FormsModule,
    InputTextModule,
    AccordionModule,
  ]
})
export class ComparisonModule { }

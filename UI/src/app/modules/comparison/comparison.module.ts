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
import { ValidationSelectorComponent } from './components/validation-selector/validation-selector.component';
import { PlotsPaginationComponent } from './components/plots-pagination/plots-pagination.component';
import {NgDompurifyModule} from "@tinkoff/ng-dompurify";
import {AccordionModule} from "primeng/accordion";

@NgModule({
    declarations: [ValidationSelectorComponent, PlotsPaginationComponent],
    exports: [
      ValidationSelectorComponent,
      PlotsPaginationComponent
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
    NgDompurifyModule,
    AccordionModule,
  ]
})
export class ComparisonModule { }

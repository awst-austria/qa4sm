import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {NgxPaginationModule} from 'ngx-pagination';
import {ComparisonPagePaginatedComponent} from './components/comparison-page-paginated/comparison-page-paginated.component';
import {RouterModule} from '@angular/router';
import {DropdownModule} from 'primeng/dropdown';
import {FormsModule} from '@angular/forms';
import {InputTextModule} from 'primeng/inputtext';
import {ValidationSelectorModule} from '../validation-selector/validation-selector.module';
import { ValidationSelectorComponent } from './components/validation-selector/validation-selector.component';

@NgModule({
    declarations: [ComparisonPagePaginatedComponent, ValidationSelectorComponent],
    exports: [
        ComparisonPagePaginatedComponent,
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
        ValidationSelectorModule
    ]
})
export class ComparisonModule { }

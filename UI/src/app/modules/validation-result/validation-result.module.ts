import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ValidationrunRowComponent} from './components/validationrun-row/validationrun-row.component';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {NgxPaginationModule} from 'ngx-pagination';
import {ValidationPagePaginatedComponent} from './components/validation-page-paginated/validation-page-paginated.component';
import {RouterModule} from '@angular/router';
import {SortingFormComponent} from './components/sorting-form/sorting-form.component';
import {DropdownModule} from 'primeng/dropdown';
import {FormsModule} from '@angular/forms';

@NgModule({
    declarations: [ValidationrunRowComponent, ValidationPagePaginatedComponent, SortingFormComponent],
  exports: [
    ValidationrunRowComponent,
    ValidationPagePaginatedComponent,
  ],
    imports: [
        CommonModule,
        PanelModule,
        TooltipModule,
        FontAwesomeModule,
        NgxPaginationModule,
        RouterModule,
        DropdownModule,
        FormsModule
    ]
})
export class ValidationResultModule { }

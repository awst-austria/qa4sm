import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ValidationrunRowComponent} from './components/validationrun-row/validationrun-row.component';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {NgxPaginationModule} from 'ngx-pagination';
import {ValidationPagePaginatedComponent} from './components/validation-page-paginated/validation-page-paginated.component';
import {RouterModule} from '@angular/router';


@NgModule({
    declarations: [ValidationrunRowComponent, ValidationPagePaginatedComponent],
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
    RouterModule
  ]
})
export class ValidationResultModule { }

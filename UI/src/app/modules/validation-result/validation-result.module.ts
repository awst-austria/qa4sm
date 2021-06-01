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
import {ValidationSummaryComponent} from './components/validation-summary/validation-summary.component';
import {ButtonsComponent} from './components/buttons/buttons.component';
import {InputTextModule} from 'primeng/inputtext';
import {TrackedValidationsComponent} from './components/tracked-validations/tracked-validations.component';
import {SummaryStatisticsComponent} from './components/summary-statistics/summary-statistics.component';
import {ResultFilesComponent} from './components/result-files/result-files.component';
import {NgDompurifyModule} from '@tinkoff/ng-dompurify';
import {ButtonModule} from 'primeng/button';

@NgModule({
  declarations: [ValidationrunRowComponent,
    ValidationPagePaginatedComponent,
    SortingFormComponent,
    ValidationSummaryComponent,
    ButtonsComponent,
    TrackedValidationsComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent],
  exports: [
    ValidationrunRowComponent,
    ValidationPagePaginatedComponent,
    ValidationSummaryComponent,
    TrackedValidationsComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent,
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
    ButtonModule
  ]
})
export class ValidationResultModule {
}

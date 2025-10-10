import {NgModule} from '@angular/core';
import {ValidationrunRowComponent} from './components/validationrun-row/validationrun-row.component';
import {
  ValidationPagePaginatedComponent
} from './components/validation-page-paginated/validation-page-paginated.component';
import {RouterModule} from '@angular/router';
import {SortingFormComponent} from './components/sorting-form/sorting-form.component';
import {ValidationSummaryComponent} from './components/validation-summary/validation-summary.component';
import {ButtonsComponent} from './components/buttons/buttons.component';
import {TrackedValidationsComponent} from './components/tracked-validations/tracked-validations.component';
import {SummaryStatisticsComponent} from './components/summary-statistics/summary-statistics.component';
import {ResultFilesComponent} from './components/result-files/result-files.component';
import {NgDompurifyModule} from '@tinkoff/ng-dompurify';
import {PublishingComponent} from './components/publishing/publishing.component';
import {ExistingValidationComponent} from './components/existing-validation/existing-validation.component';
import {
  HandleMultipleValidationsComponent
} from './components/handle-multiple-validations/handle-multiple-validations.component';
import {CoreModule} from '../core/core.module';
import {FilteringFormComponent} from './components/filtering-form/filtering-form.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [ValidationrunRowComponent,
    ValidationPagePaginatedComponent,
    SortingFormComponent,
    FilteringFormComponent,
    ValidationSummaryComponent,
    ButtonsComponent,
    TrackedValidationsComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent,
    PublishingComponent,
    ExistingValidationComponent,
    HandleMultipleValidationsComponent],
  
  exports: [
    ValidationrunRowComponent,
    ValidationPagePaginatedComponent,
    ValidationSummaryComponent,
    TrackedValidationsComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent,
    PublishingComponent,
    ExistingValidationComponent,
    ],
  imports: [
    SharedPrimeNgModule,
    RouterModule,
    NgDompurifyModule,
    CoreModule,
  ]
})
export class ValidationResultModule {
}

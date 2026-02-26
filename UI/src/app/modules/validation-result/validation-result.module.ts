import {NgModule} from '@angular/core';
import {RouterModule} from '@angular/router';
import {ValidationSummaryComponent} from './components/validation-summary/validation-summary.component';
import {ButtonsComponent} from './components/buttons/buttons.component';
import {SummaryStatisticsComponent} from './components/summary-statistics/summary-statistics.component';
import {ResultFilesComponent} from './components/result-files/result-files.component';
import {PublishingComponent} from './components/publishing/publishing.component';
import {ExistingValidationComponent} from './components/existing-validation/existing-validation.component';
import {CoreModule} from '../core/core.module';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [
    ValidationSummaryComponent,
    ButtonsComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent,
    PublishingComponent,
    ExistingValidationComponent],
  
  exports: [
    ValidationSummaryComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent,
    PublishingComponent,
    ExistingValidationComponent,
    ],
  imports: [
    SharedPrimeNgModule,
    RouterModule,
    CoreModule,
  ]
})
export class ValidationResultModule {
}

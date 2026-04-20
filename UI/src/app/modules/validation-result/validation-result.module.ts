import { NgModule } from '@angular/core';
import { ValidationrunRowComponent } from './components/validationrun-row/validationrun-row.component';
import { RouterModule } from '@angular/router';
import { ValidationSummaryComponent } from './components/validation-summary/validation-summary.component';
import { ButtonsComponent } from './components/buttons/buttons.component';
import { SummaryStatisticsComponent } from './components/summary-statistics/summary-statistics.component';
import { ResultFilesComponent } from './components/result-files/result-files.component';
import { PublishingComponent } from './components/publishing/publishing.component';
import { ExistingValidationComponent } from './components/existing-validation/existing-validation.component';
import {CoreModule} from '../core/core.module';
import { InteractiveMapComponent } from './components/interactive-map/interactive-map.component'
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [ValidationrunRowComponent,
    ValidationSummaryComponent,
    ButtonsComponent,
    SummaryStatisticsComponent,
    ResultFilesComponent,
    PublishingComponent,
    ExistingValidationComponent],
  
  exports: [
    ValidationrunRowComponent,
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
    InteractiveMapComponent
  ]
})
export class ValidationResultModule {
}

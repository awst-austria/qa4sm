import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationrunRowComponent } from './components/validationrun-row/validationrun-row.component';
import { PanelModule } from 'primeng/panel';
import { TooltipModule } from 'primeng/tooltip';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  ValidationPagePaginatedComponent
} from './components/validation-page-paginated/validation-page-paginated.component';
import { RouterModule } from '@angular/router';
import { SortingFormComponent } from './components/sorting-form/sorting-form.component';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ValidationSummaryComponent } from './components/validation-summary/validation-summary.component';
import { ButtonsComponent } from './components/buttons/buttons.component';
import { InputTextModule } from 'primeng/inputtext';
import { TrackedValidationsComponent } from './components/tracked-validations/tracked-validations.component';
import { SummaryStatisticsComponent } from './components/summary-statistics/summary-statistics.component';
import { ResultFilesComponent } from './components/result-files/result-files.component';
import { NgDompurifyModule } from '@tinkoff/ng-dompurify';
import { ButtonModule } from 'primeng/button';
import { PublishingComponent } from './components/publishing/publishing.component';
import { ExistingValidationComponent } from './components/existing-validation/existing-validation.component';
import { GalleriaModule } from 'primeng/galleria';
import { DialogModule } from 'primeng/dialog';
import {
  HandleMultipleValidationsComponent
} from './components/handle-multiple-validations/handle-multiple-validations.component';
import { PanelMenuModule } from 'primeng/panelmenu';
import { FieldsetModule } from 'primeng/fieldset';
import { CheckboxModule } from 'primeng/checkbox';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { MenuModule } from 'primeng/menu';
import { CoreModule } from '../core/core.module';
import { FilteringFormComponent } from './components/filtering-form/filtering-form.component';
import { CalendarModule } from 'primeng/calendar';
import { AccordionModule } from 'primeng/accordion';
import { ChipModule } from 'primeng/chip';
import { CardModule } from 'primeng/card';
import { Ripple } from 'primeng/ripple';
import { InteractiveMapComponent } from './components/interactive-map/interactive-map.component';

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
        CommonModule,
        PanelModule,
        TooltipModule,
        FontAwesomeModule,
        RouterModule,
        DropdownModule,
        MultiSelectModule,
        CalendarModule,
        FormsModule,
        InputTextModule,
        NgDompurifyModule,
        ButtonModule,
        ReactiveFormsModule,
        GalleriaModule,
        DialogModule,
        PanelMenuModule,
        FieldsetModule,
        CheckboxModule,
        SelectButtonModule,
        ToggleButtonModule,
        MenuModule,
        CoreModule,
        AccordionModule,
        ChipModule,
        CardModule,
        Ripple,
        InteractiveMapComponent
    ]
})
export class ValidationResultModule {
}

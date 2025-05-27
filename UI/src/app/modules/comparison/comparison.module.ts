import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PanelModule } from 'primeng/panel';
import { TooltipModule } from 'primeng/tooltip';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { RouterModule } from '@angular/router';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { ValidationSelectorComponent } from './components/validation-selector/validation-selector.component';
import { PlotsComponent } from './components/plots/plots.component';
import { AccordionModule } from 'primeng/accordion';
import { DatasetModule } from '../dataset/dataset.module';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { SpatialExtentComponent } from './components/spatial-extent/spatial-extent.component';
import { NgDompurifyModule } from '@tinkoff/ng-dompurify';
import { TableComparisonComponent } from './components/table-comparison/table-comparison.component';
import { ComparisonSummaryComponent } from './components/comparison-summary/comparison-summary.component';
import { ValidationResultModule } from '../validation-result/validation-result.module';
import { ExtentVisualizationComponent } from './components/extent-visualization/extent-visualization.component';
import { CoreModule } from '../core/core.module';
import { ImageModule } from 'primeng/image';
import { GalleriaModule } from 'primeng/galleria';

@NgModule({
  declarations: [ValidationSelectorComponent, PlotsComponent, SpatialExtentComponent, TableComparisonComponent,
    ComparisonSummaryComponent, ExtentVisualizationComponent],
  exports: [
    ValidationSelectorComponent, PlotsComponent, SpatialExtentComponent, TableComparisonComponent,
    ComparisonSummaryComponent, ExtentVisualizationComponent
  ],
  imports: [
    CommonModule,
    PanelModule,
    TooltipModule,
    FontAwesomeModule,
    RouterModule,
    DropdownModule,
    FormsModule,
    InputTextModule,
    AccordionModule,
    DatasetModule,
    ButtonModule,
    CheckboxModule,
    NgDompurifyModule,
    ValidationResultModule,
    CoreModule,
    ImageModule,
    GalleriaModule,
  ]
})
export class ComparisonModule { }

import {NgModule} from '@angular/core';
import {RouterModule} from '@angular/router';
import {ValidationSelectorComponent} from './components/validation-selector/validation-selector.component';
import {PlotsComponent} from './components/plots/plots.component';
import {DatasetModule} from '../dataset/dataset.module';
import {SpatialExtentComponent} from './components/spatial-extent/spatial-extent.component';
import {TableComparisonComponent} from './components/table-comparison/table-comparison.component';
import {ComparisonSummaryComponent} from './components/comparison-summary/comparison-summary.component';
import {ValidationResultModule} from '../validation-result/validation-result.module';
import {ExtentVisualizationComponent} from './components/extent-visualization/extent-visualization.component';
import {CoreModule} from '../core/core.module';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [ValidationSelectorComponent, PlotsComponent, SpatialExtentComponent, TableComparisonComponent,
    ComparisonSummaryComponent, ExtentVisualizationComponent, ExtentVisualizationComponent],
  exports: [
    ValidationSelectorComponent, PlotsComponent, SpatialExtentComponent, TableComparisonComponent,
    ComparisonSummaryComponent, ExtentVisualizationComponent, ExtentVisualizationComponent
  ],
  imports: [
    SharedPrimeNgModule,
    RouterModule,
    DatasetModule,
    ValidationResultModule,
    CoreModule,
  ]
})
export class ComparisonModule { }

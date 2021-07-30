import {Component, OnInit} from '@angular/core';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {HttpParams} from '@angular/common/http';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';
import {ExtentModel} from '../spatial-extent/extent-model';
import {Observable} from 'rxjs';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../../validation-result/services/dataset-configuration.service';
import {ComparisonService} from '../../services/comparison.service';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';

@Component({
  selector: 'qa-extent-visualization',
  templateUrl: './extent-visualization.component.html',
  styleUrls: ['./extent-visualization.component.scss']
})

export class ExtentVisualizationComponent implements OnInit {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [], new ExtentModel(true).getIntersection,
  );

  intersectionText: boolean
  extentImage$: Observable<string>;

  constructor(private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService,
              private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer,
              private plotService: WebsiteGraphicsService) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
        this.comparisonModel = comparison;
        this.getExtentImage(comparison);
        this.intersectionText = this.comparisonModel.getIntersection
      }
    });
  }

  getExtentImage(comparisonModel: Validations2CompareModel): void {
    // Get all the plots for a specific comparison and metric
    let parameters = new HttpParams()
      .set('get_intersection', String(comparisonModel.getIntersection));

    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    ids.forEach(id => {
      parameters = parameters.append('ids', id);
    });
    this.extentImage$ = this.comparisonService.getComparisonExtentImage(parameters);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

  downloadExtentImage(comparisonModel): void {
    // should provide a download of the comparison image
    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    this.comparisonService.downloadExtentImage(ids, comparisonModel.getIntersection);
    console.log(this.comparisonService.downloadExtentImage(ids, comparisonModel.getIntersection))
  }
}

import { Component, OnInit } from '@angular/core';
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {HttpParams} from "@angular/common/http";
import {DomSanitizer, SafeUrl} from "@angular/platform-browser";
import {ExtentModel} from "../spatial-extent/extent-model";
import {ValidationResultModel} from "../../../../pages/validation-result/validation-result-model";
import {Observable} from "rxjs";
import {PlotDto} from "../../../core/services/global/plot.dto";
import {ValidationrunService} from "../../../core/services/validation-run/validationrun.service";
import {DatasetConfigurationService} from "../../../validation-result/services/dataset-configuration.service";
import {ComparisonService} from "../../services/comparison.service";
import {WebsiteGraphicsService} from "../../../core/services/global/website-graphics.service";

@Component({
  selector: 'qa-extent-visualization',
  templateUrl: './extent-visualization.component.html',
  styleUrls: ['./extent-visualization.component.scss']
})

export class ExtentVisualizationComponent implements OnInit {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [], new ExtentModel(true).getIntersection,
  );
  isSingle: boolean = true;
  valResModels: ValidationResultModel[] = [];
  extentImage$: Observable<PlotDto>;

  constructor(private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService,
              private comparisonService: ComparisonService,
              private domSanitizer: DomSanitizer,
              private plotService: WebsiteGraphicsService,) {
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
    // console.log('img', this.extentImage$);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

  downloadExtentImage(): void {
    // should provide a download of the comparison image
  }
}

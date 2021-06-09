import { Component, OnInit } from '@angular/core';
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {ComparisonService} from '../../services/comparison.service';
import {Observable} from 'rxjs';
import {PlotDto} from '../../../core/services/global/plot.dto';
import {ExtentModel} from "../spatial-extent/extent-model";
import {ValidationResultModel} from "../../../../pages/validation-result/validation-result-model";
import {ValidationrunService} from "../../../core/services/validation-run/validationrun.service";
import {DatasetConfigurationService} from "../../../validation-result/services/dataset-configuration.service";

@Component({
  selector: 'qa-comparison-summary',
  templateUrl: './comparison-summary.component.html',
  styleUrls: ['./comparison-summary.component.scss']
})
export class ComparisonSummaryComponent implements OnInit {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [], new ExtentModel(true).getIntersection,
  );
  isSingle: boolean = true;
  valResModels: ValidationResultModel[] = [];
  extentImage$: Observable<PlotDto>;

  constructor(private validationRunService: ValidationrunService,
              private datasetConfigurationService: DatasetConfigurationService,
              private comparisonService: ComparisonService,) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
        this.comparisonModel = comparison;
        this.getValidationResultModels(comparison)
        this.isSingle = (this.comparisonModel.selectedValidations.length == 1);
      }
    });
  }

  getValidationResultModels(comparisonModel: Validations2CompareModel): void {
    // momentarily unused
    this.valResModels = []
    for (let val of comparisonModel.selectedValidations) {
      this.valResModels.push(
        new ValidationResultModel(
          this.validationRunService.getValidationRunById(val.id),
          this.datasetConfigurationService.getConfigByValidationrun(val.id)
        )
      )
    }
  }
}

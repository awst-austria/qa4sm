import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {HttpParams} from '@angular/common/http';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';
import {ExtentModel} from '../spatial-extent/extent-model';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {DatasetConfigurationService} from '../../../validation-result/services/dataset-configuration.service';
import {ComparisonService} from '../../services/comparison.service';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
// import {CarouselComponent} from 'angular-gallery/lib/carousel.component.d';
// import {Gallery} from 'angular-gallery';

@Component({
  selector: 'qa-extent-visualization',
  templateUrl: './extent-visualization.component.html',
  styleUrls: ['./extent-visualization.component.scss']
})

export class ExtentVisualizationComponent implements OnInit {
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [], new ExtentModel(true).getIntersection,
    false
  );

  @Output() isError = new EventEmitter<boolean>();
  intersectionText: boolean;
  showLoadingSpinner = true;
  errorHappened = false;
  img: string;

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
      this.comparisonModel = comparison;
      if ((comparison.selectedValidations.length > 1 && !comparison.multipleNonReference) ||
        (comparison.selectedValidations.length === 1 && comparison.multipleNonReference)) {
        this.getExtentImage(comparison);
        this.intersectionText = this.comparisonModel.getIntersection;
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
    this.comparisonService.getComparisonExtentImage(parameters).subscribe(data => {
      if (data) {
        this.img = data;
        this.showLoadingSpinner = false;
      }
    },
      () => {
        this.showLoadingSpinner = false;
        this.errorHappened = true;
        this.isError.emit(true);
      }
    );
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

}

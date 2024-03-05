import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {HttpParams} from '@angular/common/http';
import {SafeUrl} from '@angular/platform-browser';
import {ExtentModel} from '../spatial-extent/extent-model';
import {ComparisonService} from '../../services/comparison.service';
import {WebsiteGraphicsService} from '../../../core/services/global/website-graphics.service';
import {catchError} from 'rxjs/operators';
import {EMPTY, Observable} from 'rxjs';

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

  constructor(private comparisonService: ComparisonService,
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

    const getComparisonExtentImageObserver = {
      next: data => this.onGetComparisonExtentImageNext(data),
    }

    this.comparisonService.getComparisonExtentImage(parameters)
      .pipe(
        catchError(() => this.onGetComparisonExtentImageError())
      )
      .subscribe(getComparisonExtentImageObserver);
  }

  sanitizePlotUrl(plotBase64: string): SafeUrl {
    return this.plotService.sanitizePlotUrl(plotBase64);
  }

  private onGetComparisonExtentImageNext(data): void {
    if (data) {
      this.img = data;
      this.showLoadingSpinner = false;
    }
  }

  private onGetComparisonExtentImageError(): Observable<never> {
    this.showLoadingSpinner = false;
    this.errorHappened = true;
    this.isError.emit(true);
    return EMPTY;
  }

}

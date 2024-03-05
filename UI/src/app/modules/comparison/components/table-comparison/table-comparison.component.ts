import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {catchError, debounceTime} from 'rxjs/operators';
import {EMPTY, Observable} from 'rxjs';

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {
  @Output() isError = new EventEmitter<boolean>();

  comparisonParameters: HttpParams;
  table: string;
  showLoadingSpinner = true;
  errorHappened = false;
  getComparisonTableObserver = {
    next: data => this.onGetComparisonTableNext(data)
  }

  constructor(private comparisonService: ComparisonService) {
  }

  ngOnInit(): void {
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.pipe(debounceTime(2000)).subscribe(comparison => {
      if ((comparison.selectedValidations.length > 1 && !comparison.multipleNonReference) ||
        (comparison.selectedValidations.length === 1 && comparison.multipleNonReference)) {
        this.getComparisonMetrics(comparison);
      }
    });
  }

  getComparisonMetrics(comparisonModel: Validations2CompareModel): void {
    // get all the available metrics in the MetricsComparisonDto format
    const ids = this.comparisonService.getValidationsIds(comparisonModel.selectedValidations);
    // TODO: is this correct?
    let parameters = new HttpParams().set('get_intersection', String(comparisonModel.getIntersection).toString());
    ids.forEach(id => {
      parameters = parameters.append('ids', id);
    });
    this.comparisonService.getMetrics4Comparison(parameters)
      .pipe(
        catchError(() => this.getComparisonMetricsErrorHandler())
      )
      .subscribe(response => {
      if (response) {
        response.forEach(metric => {
          // comparisonMetrics.push(metric.metric_query_name);
          parameters = parameters.append('metric_list', metric.metric_query_name);
        });
        this.comparisonParameters = parameters;
        this.getComparisonTable(parameters);
      }
    });
  }

  getComparisonMetricsErrorHandler(): Observable<never>{
    this.errorHappened = true;
    this.showLoadingSpinner = false;
    return EMPTY
  }

  getComparisonTable(parameters): void {
    this.comparisonService.getComparisonTable(parameters)
      .pipe(
        catchError(() => this.onGetComparisonTableError())
      )
      .subscribe(this.getComparisonTableObserver);
  }

  private onGetComparisonTableNext(data): void {
    if (data) {
      this.table = data;
      this.showLoadingSpinner = false;
    }
  }

  private onGetComparisonTableError(): Observable<never> {
    this.showLoadingSpinner = false;
    this.errorHappened = true;
    this.isError.emit(true);
    return EMPTY
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    const ids = this.comparisonParameters.getAll('ids');
    const metricList = this.comparisonParameters.getAll('metric_list');
    const getIntersection = this.comparisonParameters.get('get_intersection') === 'true';
    // I don't know where extent comes from, so I leave it null and I handle it in the service
    const extent = null;
    this.comparisonService.downloadComparisonTableCsv(
      ids, metricList, getIntersection, extent
    );
  }
}

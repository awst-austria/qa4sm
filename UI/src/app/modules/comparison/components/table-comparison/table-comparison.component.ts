import {Component, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {Validations2CompareModel} from '../validation-selector/validation-selection.model';
import {debounceTime} from 'rxjs/operators';
import {ModalWindowService} from '../../../core/services/global/modal-window.service';

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {

  comparisonTable$: Observable<string>;
  comparisonParameters: HttpParams;
  loadingSpinner$: Observable<'open' | 'close'>;
  table: string;

  constructor(private comparisonService: ComparisonService,
              private modalService: ModalWindowService) {
  }

  ngOnInit(): void {
    this.loadingSpinner$ = this.modalService.watch();
    this.startComparison();
  }

  startComparison(): void {
    // start comparison on button click; updated recursively
    this.comparisonService.currentComparisonModel.pipe(debounceTime(2000)).subscribe(comparison => {
      if (comparison.selectedValidations.length > 0) {
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
    const comparisonMetrics = [];
    this.comparisonService.getMetrics4Comparison(parameters).subscribe(response => {
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

  getComparisonTable(parameters): void{
    this.comparisonService.getComparisonTable(parameters).subscribe(data => {
      this.table = data;
    });
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    const ids = this.comparisonParameters.getAll('ids');
    const metricList = this.comparisonParameters.getAll('metric_list');
    const getIntersection = this.comparisonParameters.get('get_intersection') === 'true';
    // I don't know where extent comes from so I leave it null and I handle it in the service
    const extent = null;
    this.comparisonService.downloadComparisonTableCsv(
      ids, metricList, getIntersection, extent
    );
  }
}

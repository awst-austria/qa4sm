import {Component, Input, OnInit} from '@angular/core';
import {ComparisonService} from "../../services/comparison.service";
import {Observable} from "rxjs";
import {MetricModel} from "../../../metrics/components/metric/metric-model";
import {HttpParams} from "@angular/common/http";
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";

@Component({
  selector: 'qa-table-comparison',
  templateUrl: './table-comparison.component.html',
  styleUrls: ['./table-comparison.component.scss']
})
export class TableComparisonComponent implements OnInit {

  @Input() comparisonModel: Validations2CompareModel;
  comparisonTable$: Observable<string>;
  // metrics to show the table/plots for
  metric_list: MetricModel[] = []
  // need to connect comparisonModel to metrics for showing and validation ids

  constructor(private comparisonService: ComparisonService,) { }

  ngOnInit(): void {
    this.getComparisonTable()
  }

  getComparisonTable(): void {
    const parameters = new HttpParams()
      .set('ids', null)
      .set('metric_list', null)
      .set('get_intersection', null)
      .set('extent', null)
    this.comparisonTable$ = this.comparisonService.getComparisonTable(parameters);
  }

  getComparisonTableAsCsv(): void {
    // button to make download
    this.comparisonService.downloadComparisonTableCsv(
      null, null,null,null
    );
  }
}

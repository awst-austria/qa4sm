import {Component, Input, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {MetricModel} from "../../../metrics/components/metric/metric-model";

@Component({
  selector: 'qa-plots',
  templateUrl: './plots.component.html',
  styleUrls: ['./plots.component.scss'],
})
export class PlotsComponent implements OnInit {

  @Input() comparisonModel: Validations2CompareModel;
  // metrics to show the table/plots for
  metric: MetricModel

  constructor(private comparisonService: ComparisonService,) {
  }

  ngOnInit(): void {
    this.getComparisonPlots();
  }

  getComparisonPlots(): void {
    const parameters = new HttpParams()
      .set('ids', String(this.comparisonModel.selectedValidations)) // should be ids instead?
      .set('get_intersection', String(this.comparisonModel.getIntersection))
      // number of non-reference datasets
      .set('metric', String(this.metric));

  }
}

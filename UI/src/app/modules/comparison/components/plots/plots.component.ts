import {Component, Input, OnInit} from '@angular/core';
import {ComparisonService} from '../../services/comparison.service';
import {HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Validations2CompareModel} from "../validation-selector/validation-selection.model";
import {MetricModel} from "../../../metrics/components/metric/metric-model";

const PLOT_TYPES =  ['boxplot', 'correlation', 'difference', 'mapplot'];

@Component({
  selector: 'qa-plots',
  templateUrl: './plots.component.html',
  styleUrls: ['./plots.component.scss'],
})
export class PlotsComponent implements OnInit {

  @Input() comparisonModel: Validations2CompareModel;
  // metrics to show the table/plots for
  comparisonMetrics: MetricModel[]
  selectedMetric: MetricModel
  comparisonPlots$: Observable<any>

  constructor(private comparisonService: ComparisonService,) {
  }

  ngOnInit(): void {
    this.getComparisonMetrics();
  }

  getComparisonPlots(): void {
    const parameters = new HttpParams()
      .set('ids', String(this.comparisonModel.selectedValidations))
      .set('plot_types', String(PLOT_TYPES))  // should be list instead?
      .set('metric', String(this.selectedMetric.value))
      .set('get_intersection', String(this.comparisonModel.getIntersection))
      .set('extent', null)

    this.comparisonPlots$ = this.comparisonService.getComparisonPlots(parameters)
  }

  getComparisonMetrics(){
    // get all the available metrics for this particular comparison configuration
  }

  getMetrics4Validation(validationId:string): void {
    // get the metrics of a specific validation (by id)
  }

  downloadResultFiles(): void {
    // download all the shown images as .png
  }

  onMetricChange(): void {
    // reinitialize getComparisonPlots
  }
}

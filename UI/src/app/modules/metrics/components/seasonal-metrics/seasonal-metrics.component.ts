import {Component, OnInit, signal} from '@angular/core';
import {SeasonalMetricModel} from "./seasonal-metric-model";

@Component({
  selector: 'qa-seasonal-metrics',
  templateUrl: './seasonal-metrics.component.html',
  styleUrls: ['./seasonal-metrics.component.scss']
})
export class SeasonalMetricsComponent implements OnInit{
  seasonalMetrics: SeasonalMetricModel[] = [];
  seasonalMetricTypes: string[] = [];
  selectedMetric = signal<SeasonalMetricModel|null>(null);
  selectedType = signal<string|null>(null);
  selectedOverlap = signal<number>(1);


  ngOnInit() {
    this.prepareSeasonalMetrics();
  }

  onMetricChange(selectedMetric: SeasonalMetricModel) {
    this.selectedMetric.set(selectedMetric)
    if (selectedMetric.metricName !== 'Default') {
      this.prepareMetricTypes();
      this.updateMetricSelection();
    } else {
      this.resetMetricSelection();
    }
  }

  private updateMetricSelection() {
    this.updateSelectedMetric(this.selectedType(), 'type');
    this.updateSelectedMetric(this.selectedOverlap(), 'overlap');
  }

  private resetMetricSelection() {
    this.updateSelectedMetric(null, 'type');
    this.updateSelectedMetric(null, 'overlap');
  }

  updateSelectedMetric(value, parameter){
    this.selectedMetric.update((metric) => {
      metric[parameter] = value;
      return metric;
    });
  }

  private prepareSeasonalMetrics(): void{
    this.seasonalMetrics.push(
      {metricName: 'Default',
        type: null,
        overlap: null,
        description: 'This is a default approach'}
    );
    this.seasonalMetrics.push({
      metricName: 'Intra Annual',
      type: null,
      overlap: null,
      description: 'This is an intra annual approach'
    });
    this.selectedMetric.set(this.seasonalMetrics[0]);
  }

  private prepareMetricTypes(){
    this.seasonalMetricTypes = ['Seasonal', 'Monthly'];
    this.selectedType.set(this.seasonalMetricTypes[0]);
  }
}

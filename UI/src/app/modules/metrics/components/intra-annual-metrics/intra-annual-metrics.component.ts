import {Component, model, OnInit, signal} from '@angular/core';
import {DropdownModule} from "primeng/dropdown";
import {InputNumberModule} from "primeng/inputnumber";
import {NgIf} from "@angular/common";
import {TooltipModule} from "primeng/tooltip";
import {FormsModule} from "@angular/forms";
import {IntraAnnualMetricModel} from "./intra-annual-metric-model";

@Component({
  selector: 'qa-intra-annual-metrics',
  standalone: true,
  imports: [
    DropdownModule,
    InputNumberModule,
    NgIf,
    TooltipModule,
    FormsModule
  ],
  templateUrl: './intra-annual-metrics.component.html',
  styleUrl: './intra-annual-metrics.component.scss'
})
export class IntraAnnualMetricsComponent implements OnInit{
  intraAnnualMetrics: IntraAnnualMetricModel[] = [];
  seasonalMetricTypes: string[] = [];
  selectedMetric = model<IntraAnnualMetricModel>()
  selectedType = signal<string|null>(null);
  selectedOverlap = signal<number>(0);


  ngOnInit() {
    this.prepareiIntraAnnualMetrics();
    console.log('Intra annual', this.selectedMetric())
  }

  onMetricChange(selectedMetric: IntraAnnualMetricModel) {
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

  private prepareiIntraAnnualMetrics(): void{
    this.intraAnnualMetrics.push(
      {metricName: 'Default',
        type: null,
        overlap: null,
        description: 'This is a default approach'}
    );
    this.intraAnnualMetrics.push({
      metricName: 'Intra-Annual',
      type: null,
      overlap: null,
      description: 'This is an intra annual approach'
    });
    this.selectedMetric.set(this.intraAnnualMetrics[0]);
  }

  private prepareMetricTypes(){
    this.seasonalMetricTypes = ['Seasonal', 'Monthly'];
    this.selectedType.set(this.seasonalMetricTypes[0]);
  }

}

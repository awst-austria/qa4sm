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
export class IntraAnnualMetricsComponent implements OnInit {
  intraAnnualMetrics: IntraAnnualMetricModel[] = [
    {
      metricName: 'Default',
      type: null,
      overlap: null,
      description: 'This is a default approach'
    },
    {
      metricName: 'Intra-Annual',
      type: null,
      overlap: null,
      description: 'This is an intra annual approach'
    }];
  intraAnnualMetricTypes: string[] = ['Seasonal', 'Monthly'];
  selectedMetric = model<IntraAnnualMetricModel>()
  selectedType = signal<string>(this.intraAnnualMetricTypes[0]);
  selectedOverlap = signal<number>(0);


  ngOnInit() {
    this.selectedMetric.set(this.intraAnnualMetrics[0]);
  }

  onMetricChange(selectedMetric: IntraAnnualMetricModel) {
    this.selectedMetric.set(selectedMetric)
    if (selectedMetric.metricName !== 'Default') {
      this.selectedType.set(this.intraAnnualMetricTypes[0]);
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

  updateSelectedMetric(value: string | number, parameter: string) {
    this.selectedMetric.update((metric) => {
      metric[parameter] = value;
      return metric;
    });
  }


}

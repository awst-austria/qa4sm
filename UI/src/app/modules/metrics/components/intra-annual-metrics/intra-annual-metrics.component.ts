import {Component, model, OnInit, signal} from '@angular/core';
import {DropdownModule} from "primeng/dropdown";
import {InputNumberModule} from "primeng/inputnumber";
import {NgIf} from "@angular/common";
import {TooltipModule} from "primeng/tooltip";
import {FormsModule} from "@angular/forms";
import {IntraAnnualMetricsDto} from "../../../../pages/validate/service/validation-run-config-dto";

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
  intraAnnualMetrics: IntraAnnualMetricsDto[] = [
    {
      name: 'Default',
      type: null,
      overlap: null,
      description: 'This is a default approach'
    },
    {
      name: 'Intra-Annual',
      type: null,
      overlap: null,
      description: 'This is an intra annual approach'
    }];
  intraAnnualMetricTypes: string[] = ['Seasonal', 'Monthly'];
  selectedMetric = model<IntraAnnualMetricsDto>()
  selectedType = signal<string>(this.intraAnnualMetricTypes[0]);
  selectedOverlap = signal<number>(0);


  ngOnInit() {
    this.selectedMetric.set(this.intraAnnualMetrics[0]);
  }

  onMetricChange(selectedMetric: IntraAnnualMetricsDto) {
    this.selectedMetric.set(selectedMetric)
    if (selectedMetric.name !== 'Default') {
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

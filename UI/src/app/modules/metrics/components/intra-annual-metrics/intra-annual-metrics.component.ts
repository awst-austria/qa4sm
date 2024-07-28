import {Component, model, OnInit, signal} from '@angular/core';
import {DropdownModule} from "primeng/dropdown";
import {InputNumberModule} from "primeng/inputnumber";
import {NgIf} from "@angular/common";
import {TooltipModule} from "primeng/tooltip";
import {FormsModule} from "@angular/forms";
import {IntraAnnualMetricsDto} from "../../../../pages/validate/service/validation-run-config-dto";
import {CheckboxModule} from "primeng/checkbox";

@Component({
  selector: 'qa-intra-annual-metrics',
  standalone: true,
  imports: [
    DropdownModule,
    InputNumberModule,
    NgIf,
    TooltipModule,
    FormsModule,
    CheckboxModule
  ],
  templateUrl: './intra-annual-metrics.component.html',
  styleUrl: './intra-annual-metrics.component.scss'
})
export class IntraAnnualMetricsComponent implements OnInit {


  intraAnnualMetricTypes: string[] = ['Seasonal', 'Monthly'];
  metricSelected = signal(false);
  selectedMetric = model<IntraAnnualMetricsDto>()
  selectedType = signal<string>(this.intraAnnualMetricTypes[0]);
  selectedOverlap = signal<number>(0);


  ngOnInit() {
    console.log('Monika')
    // this.selectedMetric.set(this.intraAnnualMetrics[0]);
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

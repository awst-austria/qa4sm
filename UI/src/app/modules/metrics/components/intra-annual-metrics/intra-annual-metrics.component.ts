import {Component, input, model, signal} from '@angular/core';
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
export class IntraAnnualMetricsComponent {

  intraAnnualMetricTypes: string[] = ['Seasonal', 'Monthly', 'Custom'];
  defaultOverlaps: number[] = [30, 1];
  maxOverlaps: number[] = [185, 15];

  defaultIntraAnnualOverlap = signal(30);
  maxIntraAnnualOverlap = signal(185);
  disabled = input<boolean>();
  selectedMetric = model<IntraAnnualMetricsDto | null>(null)


  updateType(value: string) {
    this.selectedMetric.update((metric) => {
      metric.intra_annual_type = value;

      const ind = this.intraAnnualMetricTypes.indexOf(value);
      this.defaultIntraAnnualOverlap.set(this.defaultOverlaps[ind]);
      this.maxIntraAnnualOverlap.set(this.maxOverlaps[ind]);

      this.setOverlap(this.defaultOverlaps[ind]);

      return metric;
    });
  }

  setOverlap(value: number) {
    this.selectedMetric.update((metric) => {
      metric.intra_annual_overlap = value;
      return metric;
    });
  }

  toggleMetricSelection(value: boolean) {
    this.selectedMetric.update((metric) => {
      metric.intra_annual_metrics = value;


      if (value) {
        metric.intra_annual_type = this.intraAnnualMetricTypes[0];
        metric.intra_annual_overlap = this.defaultIntraAnnualOverlap();
      } else {
        metric.intra_annual_overlap = null;
        metric.intra_annual_type = null;
      }

      return metric;
    });
  }


}

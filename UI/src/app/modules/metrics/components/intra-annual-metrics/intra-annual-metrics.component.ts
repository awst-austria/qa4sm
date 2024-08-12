import {Component, model} from '@angular/core';
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

  intraAnnualMetricTypes: string[] = ['Seasonal', 'Monthly'];
  defaultIntraAnnualOverlap: number = 30;
  selectedMetric = model<IntraAnnualMetricsDto>()


  updateSelectedMetric(value: string | number | boolean, parameter: string) {
    this.selectedMetric.update((metric) => {
      metric[parameter] = value;

      if (parameter === 'intra_annual_metrics') {
        if (value) {
          metric.intra_annual_type = this.intraAnnualMetricTypes[0];
          metric.intra_annual_overlap = this.defaultIntraAnnualOverlap;
        } else {
          metric.intra_annual_overlap = null;
          metric.intra_annual_type = null;
        }
      }

      return metric;
    });
  }


}

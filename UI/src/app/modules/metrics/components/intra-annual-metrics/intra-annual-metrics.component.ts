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
  selectedMetric = model<IntraAnnualMetricsDto>()

  updateSelectedMetric(value: string | number, parameter: string) {
    this.selectedMetric.update((metric) => {
      metric[parameter] = value;
      return metric;
    });
  }


}

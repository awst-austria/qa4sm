import { Component, Input, model, signal } from '@angular/core';
import { InputNumberModule } from 'primeng/inputnumber';
import { NgIf } from '@angular/common';
import { TooltipModule } from 'primeng/tooltip';
import { FormsModule } from '@angular/forms';
import { IntraAnnualMetricsDto } from '../../../../pages/validate/service/validation-run-config-dto';
import { CheckboxModule } from 'primeng/checkbox';
import { Select } from 'primeng/select';

@Component({
  selector: 'qa-intra-annual-metrics',
  standalone: true,
  imports: [
    InputNumberModule,
    NgIf,
    TooltipModule,
    FormsModule,
    CheckboxModule,
    Select
  ],
  templateUrl: './intra-annual-metrics.component.html',
  styleUrl: './intra-annual-metrics.component.scss'
})
export class IntraAnnualMetricsComponent {
  @Input() disabled: boolean = false;

  intraAnnualMetricTypes: string[] = ['Seasonal', 'Monthly'];

  defaultOverlaps: number[] = [0, 0];
  maxOverlaps: number[] = [45, 15];


  defaultIntraAnnualOverlap = signal(0);
  maxIntraAnnualOverlap = signal(45);
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

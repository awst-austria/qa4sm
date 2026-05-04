import { Component, Input, OnInit } from '@angular/core';
import { ValidationrunDto } from 'src/app/modules/core/services/validation-run/validationrun.dto';
import { Observable } from 'rxjs';
import { ValidationrunService } from 'src/app/modules/core/services/validation-run/validationrun.service';
import { GlobalParamsService } from 'src/app/modules/core/services/global/global-params.service';
import { HttpParams } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { PanelModule } from 'primeng/panel';
import { Tooltip } from 'primeng/tooltip';

@Component({
  selector: 'qa-summary-statistics-spatial',
  imports: [CommonModule, ButtonModule, PanelModule, Tooltip],
  templateUrl: './summary-statistics-spatial.component.html',
  styleUrl: './summary-statistics-spatial.component.scss',
})

export class SummaryStatisticsSpatialComponent implements OnInit {
  @Input() validationRun: ValidationrunDto;
  table$: Observable<string>;

  constructor(
    private validationService: ValidationrunService,
    public globals: GlobalParamsService,
  ) {}

  ngOnInit(): void {
    this.getSummaryStatistics();
  }

  getSummaryStatistics(): void {
    const parameters = new HttpParams().set('id', this.validationRun.id);
    this.table$ = this.validationService.getSummaryStatisticsSpatial(parameters);
  }

  getSummaryStatisticsAsCsv(): void {
    this.validationService.downloadSpatialResultFile(
      this.validationRun.id,
      'statistics',
      `${this.validationRun.id}_spatial_statistics.zip`
    );
  }
}
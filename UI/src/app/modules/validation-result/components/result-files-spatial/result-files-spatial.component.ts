import { CommonModule, JsonPipe } from '@angular/common';
import { HttpParams } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { PanelModule } from 'primeng/panel';
import { ValidationrunDto } from 'src/app/modules/core/services/validation-run/validationrun.dto';
import { ValidationrunService } from 'src/app/modules/core/services/validation-run/validationrun.service';

@Component({
  selector: 'qa-result-files-spatial',
  imports: [CommonModule, JsonPipe, PanelModule, ButtonModule],
  templateUrl: './result-files-spatial.component.html',
  styleUrl: './result-files-spatial.component.scss',
})
export class ResultFilesSpatialComponent implements OnInit{
  @Input() validation: ValidationrunDto;

  spatialMetrics: any = null;
  spatialFileInfo: any = null;
  loading = true;
  error: string = null;

  constructor(private validationService: ValidationrunService) {}

  ngOnInit(): void {
    this.loadSpatialData();
  }

  private loadSpatialData(): void {
    const params = new HttpParams().set('validationId', this.validation.id);

    // проверяем файл
    this.validationService.getMetricsAndPlotsNamesSpatial(params).subscribe({
      next: (data) => {
        this.spatialMetrics = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = JSON.stringify(err);
        this.loading = false;
      }
    });
  }

  downloadSpatialNetCDF(): void {
    this.validationService.downloadSpatialResultFile(this.validation.id, 'netCDF', 'spatial.nc');
  }

  downloadSpatialGraphics(): void {
      this.validationService.downloadSpatialResultFile(this.validation.id, 'graphics', 'spatial_graphs.zip');
  }

  downloadSpatialStatistics(): void {
      this.validationService.downloadSpatialResultFile(this.validation.id, 'statistics', 'spatial_statistics.zip');
  }

}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

// PrimeNG
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';

import { HttpParams } from '@angular/common/http';
import { Subject } from 'rxjs';
import { switchMap, startWith, catchError } from 'rxjs/operators';

import { ValidationrunService } from '../../../core/services/validation-run/validationrun.service';
import { ValidationrunDto } from '../../../core/services/validation-run/validationrun.dto';
import { FilterConfig } from 'src/app/modules/validation-result/components/filtering-form/filter-payload.interface';
import { DatasetService } from '../../../core/services/dataset/dataset.service';
import { DatasetDto } from '../../../core/services/dataset/dataset.dto';
import { DatasetVersionService } from '../../../core/services/dataset/dataset-version.service';
import { DatasetVersionDto } from '../../../core/services/dataset/dataset-version.dto';
import { DatasetConfigurationService } from '../../services/dataset-configuration.service';
import { of } from 'rxjs';

@Component({
  selector: 'qa-my-validations',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    TableModule,
    ButtonModule,
    CheckboxModule
    
  ],
  templateUrl: './my-validations.component.html',
  styleUrls: ['./my-validations.component.scss'],
})
export class MyValidationsComponent implements OnInit {
  validations: ValidationrunDto[] = [];
  selectedValidations: ValidationrunDto[] = [];

  valFilters: FilterConfig[] = [];
  order = 'start_time:desc';

  isLoading = false;
  dataFetchError = false;

  datasetsList: DatasetDto[] = [];
  versionsCache: DatasetVersionDto[] = [];

  private reload$ = new Subject<void>();

  constructor(
    private validationrunService: ValidationrunService,
    private datasetService: DatasetService,
    private datasetVersionService: DatasetVersionService,
    private datasetConfigService: DatasetConfigurationService
  ) {}

  ngOnInit(): void {
    // справочники
    this.datasetService.getAllDatasets(true, false)
      .subscribe(ds => this.datasetsList = ds || []);

    this.datasetVersionService.getAllVersions()
      .subscribe(vs => this.versionsCache = vs || []);

    // реакция на внешние refresh-события
    this.validationrunService.doRefresh$
      .subscribe(() => this.reload());

    // первый запуск
    this.reload();

    // подписка на reload$
    this.reload$
      .pipe(
        startWith(void 0),
        switchMap(() => {
          this.isLoading = true;
          const params = this.getHttpParams();
          return this.validationrunService.getMyValidationruns(params)
            .pipe(
              catchError(err => {
                this.dataFetchError = true;
                this.isLoading = false;
                // ВАЖНО: вернуть объект такой же формы, как успешный ответ
                return of({ validations: [], length: 0 });
              })
            );
        }),
      )
      .subscribe((response: { validations: ValidationrunDto[]; length: number }) => {
        const { validations, length } = response;

        validations.forEach(v => {
          this.setReferenceNamesForValidation(v);
        });

        this.validations = validations;
        this.isLoading = false;
        this.dataFetchError = false;
      });
  }

  private getHttpParams(): HttpParams {
    let params = new HttpParams()
      .set('offset', '0')
      .set('limit', '50')
      .set('order', this.order);

    this.valFilters.forEach(filter => {
      params = params.set('filter:' + filter.backendName, filter.selectedOptions().toString());
    });

    return params;
  }

  reload(): void {
    this.reload$.next();
  }

  getStatusFromProgress(valrun: ValidationrunDto): string {
    if (valrun.progress === 0 && valrun.end_time === null) {
      return 'Scheduled';
    } else if (valrun.progress === 100 && valrun.end_time) {
      return 'Done';
    } else if (valrun.progress === -1 || valrun.progress === -100) {
      return 'Cancelled';
    } else if (valrun.end_time != null || valrun.total_points == 0) {
      return 'ERROR';
    } else {
      return 'Running ' + `${valrun.progress}%`;
    }
  }

  deleteSelectedValidations(): void {
    const ids = this.selectedValidations.map(v => v.id);
    if (!ids.length) return;

    // TODO: реальный delete через сервис
    // this.validationrunService.deleteValidations(ids).subscribe(() => this.reload());

    this.validations = this.validations.filter(v => !ids.includes(v.id));
    this.selectedValidations = [];
  }

  private getVersionName(versionId?: number): string {
    if (!versionId) return '';
    const found = this.versionsCache.find(v => v.id === versionId);
    return found?.pretty_name || `v${versionId}`;
  }

  private setReferenceNamesForValidation(v: ValidationrunDto): void {
    if (!v.temporal_reference_configuration && !v.spatial_reference_configuration) {
      (v as any).temporalReference = '—';
      (v as any).spatialReference = '—';
      (v as any).temporalVersion = '';
      (v as any).spatialVersion = '';
      return;
    }

    this.datasetConfigService.getConfigByValidationrun(v.id)
      .subscribe(configs => {
        const temporalConfig = configs.find(c => c.id === v.temporal_reference_configuration);
        const spatialConfig = configs.find(c => c.id === v.spatial_reference_configuration);

        const getDatasetName = (config: any): string => {
          if (!config) return '—';
          const ds = this.datasetsList.find(d => d.id === config.dataset);
          return ds?.pretty_name || `#${config.id}`;
        };

        (v as any).temporalReference = getDatasetName(temporalConfig);
        (v as any).spatialReference = getDatasetName(spatialConfig);
        (v as any).temporalVersion = this.getVersionName(temporalConfig?.version);
        (v as any).spatialVersion = this.getVersionName(spatialConfig?.version);
      });
  }
}

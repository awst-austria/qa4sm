import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpParams } from '@angular/common/http';
import { RouterModule } from '@angular/router';

import { forkJoin, BehaviorSubject, combineLatest, of } from 'rxjs';
import { switchMap, map, catchError, shareReplay, debounceTime, distinctUntilChanged} from 'rxjs/operators';

import { DatePickerModule } from 'primeng/datepicker';
import { FloatLabelModule } from 'primeng/floatlabel';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { FormsModule } from '@angular/forms';

import { ValidationrunService } from '../../modules/core/services/validation-run/validationrun.service';
import { ValidationrunDto } from '../../modules/core/services/validation-run/validationrun.dto';

import { DatasetConfigurationService } from '../../modules/validation-result/services/dataset-configuration.service';
import { DatasetService } from '../../modules/core/services/dataset/dataset.service';
import { DatasetVersionService } from '../../modules/core/services/dataset/dataset-version.service';
import { DatasetVariableService } from '../../modules/core/services/dataset/dataset-variable.service';

import { DatasetDto } from '../../modules/core/services/dataset/dataset.dto';
import { DatasetVersionDto } from '../../modules/core/services/dataset/dataset-version.dto';
import { DatasetVariableDto } from '../../modules/core/services/dataset/dataset-variable.dto';

interface DateRange {
  from: Date | null;
  to: Date | null;
}

interface SortState {
  field: string;
  order: number; // 1 = asc, -1 = desc
}

interface Dictionaries {
  datasets: DatasetDto[];
  versions: DatasetVersionDto[];
  variables: DatasetVariableDto[];
}

@Component({
  selector: 'qa-published-validations',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    TableModule,
    InputTextModule,
    DatePickerModule,
    FloatLabelModule,
    FormsModule
  ],
  templateUrl: './published-validations.component.html',
  styleUrls: ['./published-validations.component.scss'],
})
export class PublishedValidationsComponent implements OnInit {

  // ---- reactive filters ----
  private dateFilter$ = new BehaviorSubject<DateRange>({ from: null, to: null });

  private nameFilterInput$ = new BehaviorSubject<string>('');
  private nameFilter$ = this.nameFilterInput$.pipe(
    map(v => v.trim()),
    debounceTime(300),
    distinctUntilChanged()
  );

  private datasetFilterInput$ = new BehaviorSubject<string>('');
  private datasetFilter$ = this.datasetFilterInput$.pipe(
    map(v => v.trim()),
    debounceTime(300),
    distinctUntilChanged()
  );

  readonly PAGE_SIZE = 20;
  private page$ = new BehaviorSubject<{ page: number; rows: number }>({
    page: 0,
    rows: this.PAGE_SIZE
  });

  // sort
  sortState: SortState = { field: 'start_time', order: -1 };
  private sort$ = new BehaviorSubject<SortState>(this.sortState);

  // data for table
  rows$ = of<ValidationrunDto[]>([]);
  totalRecords$ = of(0);
  isLoading = false;
  dataFetchError = false;

  // for date-picker
  dateRangeModel: Date[] | null = null;

  constructor(
    private validationrunService: ValidationrunService,
    private datasetConfigService: DatasetConfigurationService,
    private datasetService: DatasetService,
    private datasetVersionService: DatasetVersionService,
    private datasetVariableService: DatasetVariableService
  ) {}

  ngOnInit(): void {
    // 1) Load dictionaries once and cache the result
    const dictionaries$ = forkJoin({
      datasets: this.datasetService.getAllDatasets(true, false),
      versions: this.datasetVersionService.getAllVersions(),
      variables: this.datasetVariableService.getAllVariables()
    }).pipe(
      map(dicts => ({
        datasets: dicts.datasets || [],
        versions: dicts.versions || [],
        variables: dicts.variables || []
      })),
      shareReplay(1)
    );

    // 2) Main stream: dictionaries + filters + pagination + sorting
    const response$ = combineLatest([
      dictionaries$,
      this.nameFilter$,
      this.datasetFilter$,
      this.dateFilter$,
      this.page$,
      this.sort$
    ]).pipe(
      switchMap(([dicts, name, dataset, dateRange, page, sort]) => {
        this.isLoading = true;

        const params = this.buildHttpParams(name, dataset, dateRange, page.page, page.rows, sort);

        return this.validationrunService.getPublishedValidationruns(params).pipe(
          catchError(err => {
            this.dataFetchError = true;
            this.isLoading = false;
            return of({ validations: [], length: 0 });
          }),
          //  at this point we already have { validations, length }
          switchMap(res =>
            this.addDatasetsInfo(res.validations, dicts).pipe(
              map(validationsWithDatasets => ({
                ...res,
                validations: validationsWithDatasets
              }))
            )
          )
        );
      }),
      shareReplay(1)
    );

    this.rows$ = response$.pipe(
      map(res => {
        this.isLoading = false;
        this.dataFetchError = false;
        return res.validations;
      })
    );

    this.totalRecords$ = response$.pipe(
      map(res => res.length ?? 0)
    );
  }

  /* template event handlers */

  onNameFilterChange(value: string): void {
  this.nameFilterInput$.next(value);
  this.page$.next({ page: 0, rows: this.page$.value.rows }); 
  }

  onDatasetFilterChange(value: string): void {
    this.datasetFilterInput$.next(value);
    this.page$.next({ page: 0, rows: this.page$.value.rows });
  }

  onDateFilterChange(range: Date[] | null): void {
    const from = range && range[0] ? range[0] : null;
    const to = range && range[1] ? range[1] : null;

    this.dateFilter$.next({ from, to });
    this.page$.next({ page: 0, rows: this.page$.value.rows });
  }

  onPageChange(event: { first: number; rows: number; page?: number; pageCount?: number }): void {
    console.log('PAGE EVENT', event);
    const pageIndex = event.first / event.rows;  // 0,1,2,...
    this.page$.next({ page: pageIndex, rows: event.rows });
  }

  onSortChange(event: { field: string; order: number }): void {
    this.sortState = { field: event.field, order: event.order ?? 1 };
    this.sort$.next(this.sortState);
    this.page$.next({ page: 0, rows: this.PAGE_SIZE });
  }

  /* private helper methods */

  private formatLocalDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
  }

  private buildHttpParams(
    name: string,
    dataset: string,
    dateRange: DateRange,
    page: number,
    rows: number,
    sort: SortState
    ): HttpParams {
    let params = new HttpParams()
      .set('offset', String(page * rows))
      .set('limit', String(rows))
      .set('order', this.mapSortToOrder(sort));

    if (name) {
      params = params.set('filter:name', name);
    }

    if (dataset) {
      params = params.set('filter:dataset', dataset);
    }

    if (dateRange.from && dateRange.to) {
      params = params.set(
        'filter:start_time',
        `${this.formatLocalDate(dateRange.from)},${this.formatLocalDate(dateRange.to)}`
      );
    }

    return params;
  }

  private mapSortToOrder(sort: SortState): string {
    const direction = sort.order === 1 ? 'asc' : 'desc';

    switch (sort.field) {
      case 'start_time':
        return `start_time:${direction}`;
      case 'name_tag':
        return `name:${direction}`;  // ORDER_DICT в Django
      case 'spatial_reference_dataset':
        return `spatial_reference_dataset:${direction}`;
      default:
        return 'start_time:desc';
    }
  }
  
  /* For each validation, load dataset configurations and build display summary */
  private addDatasetsInfo(
    validations: ValidationrunDto[],
    dicts: Dictionaries) 
  {
    if (!validations.length) {
      return of<ValidationrunDto[]>([]);
    }

    const { datasets, versions, variables } = dicts;

    const toText = (d?: { dataset: string; version: string; variable: string; unit?: string } | null): string => {
      if (!d) return '—';
      const unit = d.unit ? ` [${d.unit}]` : '';
      return `${d.dataset} — ${d.version}, ${d.variable}${unit}`;
    };

    const resolveCfg = (cfg: any): { dataset: string; version: string; variable: string; unit?: string } => {
      const ds = datasets.find(d => d.id === cfg.dataset);
      const ver = versions.find(vv => vv.id === cfg.version);
      const variable = variables.find(vv => vv.id === cfg.variable);

      return {
        dataset: (ds as any)?.pretty_name ?? (ds as any)?.short_name ?? String(cfg.dataset),
        version: (ver as any)?.pretty_name ?? (ver as any)?.short_name ?? String(cfg.version),
        variable: (variable as any)?.pretty_name ?? (variable as any)?.short_name ?? String(cfg.variable),
        unit: (variable as any)?.unit ?? cfg.variableUnit ?? ''
      };
    };

    const obsArray = validations.map(v =>
      this.datasetConfigService.getConfigByValidationrun(v.id).pipe(
        map((configs: any[]) => {
            // 1)  Full list of datasets (for the "Datasets" column)
            const display = (configs || []).map(cfg => resolveCfg(cfg));
            (v as any).datasetsDisplay = display;

            // 2) Spatial reference (take the config with is_spatial_reference flag)
            const spatialCfg = (configs || []).find(c => c.is_spatial_reference);
            const spatialDisplay = spatialCfg ? resolveCfg(spatialCfg) : null;

            (v as any).spatialReferenceDisplay = spatialDisplay;
            (v as any).spatialReferenceText = toText(spatialDisplay);

            // 3) (Optional) Temporal reference — for future use if needed
            const temporalCfg = (configs || []).find(c => c.is_temporal_reference);
            const temporalDisplay = temporalCfg ? resolveCfg(temporalCfg) : null;

            (v as any).temporalReferenceDisplay = temporalDisplay;
            (v as any).temporalReferenceText = toText(temporalDisplay);

            return v;
          }),

        catchError(() => {
            // If dataset configs fail to load for a single validation,
            // do not break the table rendering
            (v as any).datasetsDisplay = [];
            (v as any).spatialReferenceText = '—';
            (v as any).temporalReferenceText = '—';
            return of(v);
          })
        )
      );
      return forkJoin(obsArray);
  }
  
}

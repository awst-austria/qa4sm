import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpParams } from '@angular/common/http';
import { RouterModule } from '@angular/router';

import { Observable, forkJoin, BehaviorSubject, combineLatest, of } from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, finalize, map, shareReplay, startWith, switchMap } from 'rxjs/operators';

import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';

import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { FloatLabelModule } from 'primeng/floatlabel';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { TooltipModule } from 'primeng/tooltip';

import { ValidationrunService } from '../../modules/core/services/validation-run/validationrun.service';
import { ValidationrunDto } from '../../modules/core/services/validation-run/validationrun.dto';

import { DatasetConfigurationService } from '../../modules/validation-result/services/dataset-configuration.service';
import { DatasetService } from '../../modules/core/services/dataset/dataset.service';
import { DatasetVersionService } from '../../modules/core/services/dataset/dataset-version.service';
import { DatasetVariableService } from '../../modules/core/services/dataset/dataset-variable.service';

import { DatasetDto } from '../../modules/core/services/dataset/dataset.dto';
import { DatasetVersionDto } from '../../modules/core/services/dataset/dataset-version.dto';
import { DatasetVariableDto } from '../../modules/core/services/dataset/dataset-variable.dto';

import {AuthService} from '../../modules/core/services/auth/auth.service';

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
    ButtonModule,
    CommonModule,
    RouterModule,
    TableModule,
    TooltipModule,
    InputTextModule,
    DatePickerModule,
    FloatLabelModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './published-validations.component.html',
  styleUrls: ['./published-validations.component.scss'],
})
export class PublishedValidationsComponent implements OnInit {

  // UI state
  loading = false;
  dataFetchError = false;

  // Table streams
  rows$!: Observable<ValidationrunDto[]>;
  totalRecords$!: Observable<number>;

  // Auth stream (for Pin column)
  isLogged$!: Observable<boolean>;

  // Filters form 
  filterForm!: FormGroup;

  // paging & sorting (table emits these events)
  readonly PAGE_SIZE = 20;
  private page$ = new BehaviorSubject<{ page: number; rows: number }>({ page: 0, rows: this.PAGE_SIZE });

  sortState: SortState = { field: 'start_time', order: -1 };
  private sort$ = new BehaviorSubject<SortState>(this.sortState);

  constructor(
    private fb: FormBuilder,
    private validationrunService: ValidationrunService,
    private datasetConfigService: DatasetConfigurationService,
    private datasetService: DatasetService,
    private datasetVersionService: DatasetVersionService,
    private datasetVariableService: DatasetVariableService,
    private authService: AuthService
  ) {
    this.isLogged$ = this.authService.authenticated.asObservable();
  }

  ngOnInit(): void {

    // 1) reactive form for filters
    this.filterForm = this.fb.group({
      dateRange: [null as Date[] | null], // PrimeNG range datepicker -> Date[] | null
      name: [''],
      dataset: ['']
    });

    const filters$ = this.filterForm.valueChanges.pipe(
      startWith(this.filterForm.value),
      debounceTime(300),
      map(v => {
        const range: Date[] | null = v?.dateRange ?? null;
        const from = range?.[0] ?? null;
        const to = range?.[1] ?? null;

        return {
          name: (v?.name ?? '').trim(),
          dataset: (v?.dataset ?? '').trim(),
          dateRange: { from, to } as DateRange
        };
      }),
      // simple deep-compare for a small object
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      // whenever filter changes -> reset to first page
      // (important: do this with side-effect but keep stream pure)
      switchMap(f => {
        this.page$.next({ page: 0, rows: this.page$.value.rows });
        return of(f);
      }),
      shareReplay(1)
    );


    // 2) Load dictionaries once and cache
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

    // 3) Main stream: dictionaries + filters + pagination + sorting -> request
    const response$ = combineLatest([dictionaries$, filters$, this.page$, this.sort$]).pipe(
      switchMap(([dicts, f, page, sort]) => {
        this.loading = true;
        this.dataFetchError = false;

        const params = this.buildHttpParams(
          f.name,
          f.dataset,
          f.dateRange,
          page.page,
          page.rows,
          sort
        );

        return this.validationrunService.getPublishedValidationruns(params).pipe(
          switchMap(res =>
            this.addDatasetsInfo(res.validations, dicts).pipe(
              map(validationsWithDatasets => ({
                ...res,
                validations: validationsWithDatasets
              }))
            )
          ),
          catchError(() => {
            this.dataFetchError = true;
            return of({ validations: [], length: 0 });
          }),
          finalize(() => {
            this.loading = false;
          })
        );
      }),
      shareReplay(1)
    );

    // 4) Table bindings
    this.rows$ = response$.pipe(map(res => res.validations));
    this.totalRecords$ = response$.pipe(map(res => res.length ?? 0));

  }

  
  // Pin helpers (debug-safe)
  isTrackedByTheUser(row: ValidationrunDto): boolean {
    const copied = this.authService.currentUser?.copied_runs ?? [];
    // protect against number/string mismatch
    return copied.map(String).includes(String(row.id));
  }

  onPin(row: ValidationrunDto, event: Event) {
  event.stopPropagation();

  const copied = this.authService.currentUser?.copied_runs ?? [];
  this.authService.currentUser.copied_runs = [...copied, String(row.id)];

  this.validationrunService.addValidation(row.id).subscribe({
    next: () => this.authService.init(), 
    error: () => {
      this.authService.currentUser.copied_runs = copied;
    }
    });
  }

  onUnpin(row: ValidationrunDto, event: Event) {
    event.stopPropagation();

    const copied = this.authService.currentUser?.copied_runs ?? [];
    const next = copied.filter(id => String(id) !== String(row.id));
    this.authService.currentUser.copied_runs = next;

    this.validationrunService.removeValidation(row.id).subscribe({
      next: () => this.authService.init(),
      error: () => {
        this.authService.currentUser.copied_runs = copied;
      }
    });
  }


  // p-table events
  onPageChange(event: { first: number; rows: number; page?: number; pageCount?: number }): void {
    const pageIndex = event.first / event.rows;
    this.page$.next({ page: pageIndex, rows: event.rows });
  }

  onSortChange(event: { field: string; order: number }): void {
    this.sortState = { field: event.field, order: event.order ?? 1 };
    this.sort$.next(this.sortState);
    this.page$.next({ page: 0, rows: this.PAGE_SIZE });
  }

  // Helpers
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

    if (name) params = params.set('filter:name', name);
    if (dataset) params = params.set('filter:dataset', dataset);

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
        return `name:${direction}`;
      case 'spatial_reference_dataset':
        return `spatial_reference_dataset:${direction}`;
      default:
        return 'start_time:desc';
    }
  }

  // Dataset display enrich
  private addDatasetsInfo(validations: ValidationrunDto[], dicts: Dictionaries) {
    if (!validations.length) return of<ValidationrunDto[]>([]);

    const { datasets, versions, variables } = dicts;

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
          const display = (configs || []).map(cfg => resolveCfg(cfg));
          (v as any).datasetsDisplay = display;

          const spatialCfg = (configs || []).find(c => c.is_spatial_reference);
          (v as any).spatialReferenceDisplay = spatialCfg ? resolveCfg(spatialCfg) : null;

          return v;
        }),
        catchError(() => {
          (v as any).datasetsDisplay = [];
          (v as any).spatialReferenceDisplay = null;
          return of(v);
        })
      )
    );

    return forkJoin(obsArray);
  }
}
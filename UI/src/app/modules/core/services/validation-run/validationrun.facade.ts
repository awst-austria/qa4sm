import { Injectable, inject } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import { BehaviorSubject, combineLatest, forkJoin, of, Observable, from, merge } from 'rxjs';
import { map, switchMap, catchError, shareReplay, finalize, tap, mergeMap, scan } from 'rxjs/operators';

import { ValidationrunService } from './validationrun.service';
import { DatasetService } from '../dataset/dataset.service';
import { DatasetVersionService } from '../dataset/dataset-version.service'; 
import { DatasetVariableService } from '../dataset/dataset-variable.service';
import { DatasetConfigurationService } from '../../../validation-result/services/dataset-configuration.service';



// Data structure for mapping ID-based records of ValidationRuns.
interface Dictionaries {
  datasets: Map<number, any>;
  versions: Map<number, any>;
  variables: Map<number, any>;
}

@Injectable({ providedIn: 'root' })
export class ValidationRunFacade {
  private validationService = inject(ValidationrunService);
  private datasetConfigService = inject(DatasetConfigurationService);
  private datasetService = inject(DatasetService);
  private datasetVersionService = inject(DatasetVersionService); 
  private variableService = inject(DatasetVariableService);

  // Observable tracking the loading state of validationrun  data requests
  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$ = this.loadingSubject.asObservable();

  // Local cache to store dataset configurations per validation run.
  //Prevents redundant API calls when switching between views.
  private configCache = new Map<string, any[]>();

  // Loads and caches metadata dictionaries once per session.
  private dictionaries$: Observable<Dictionaries> = forkJoin({
    datasets: this.datasetService.getAllDatasets(true, false),
    versions: this.datasetVersionService.getAllVersions(),
    variables: this.variableService.getAllVariables()
  }).pipe(
    map(res => ({
      datasets: new Map<number, any>(res.datasets.map((d: any) => [d.id, d])),
      versions: new Map<number, any>(res.versions.map((v: any) => [v.id, v])),
      variables: new Map<number, any>(res.variables.map((v: any) => [v.id, v]))
    })),
    shareReplay({ bufferSize: 1, refCount: true }) 
  );

  private getConfigsCached$(validationId: string): Observable<any[]> {
    if (this.configCache.has(validationId)) {
      return of(this.configCache.get(validationId)!);
    }
    return this.datasetConfigService.getConfigByValidationrun(validationId).pipe(
      tap(cfgs => this.configCache.set(validationId, cfgs))
    );
  }

  /**
   * Fetches validation runs and enriches them with full dataset/version/variable names.
   * Handles pagination, filtering, and caching automatically.
   * * @param mode - Source of validations: 'published' or 'user' (My Validations)
   * * @param params - HttpParams containing filters, sorting, and pagination
   */
  getValidations(
    mode: 'published' | 'user',
    params: HttpParams
  ): Observable<{ rows: any[]; total: number }> {

    this.loadingSubject.next(true);
    
    const apiCall$ = mode === 'published'
      ? this.validationService.getPublishedValidationruns(params)
      : this.validationService.getMyValidationruns(params);

    return combineLatest([this.dictionaries$, apiCall$]).pipe(
      switchMap(([dicts, response]) => {
        const total = response.length ?? 0;

        if (!response.validations?.length) {
          this.loadingSubject.next(false);
          return of({ rows: [], total });
        }

        // Display validations-runs rows
        const baseRows = response.validations.map(v => ({
          ...v,
          datasetsDisplay: [],
          spatialReferenceDisplay: null
        }));

        this.loadingSubject.next(false);

        // provide each row with dataset information
        const patches$ = from(baseRows).pipe(
          mergeMap((v: any) =>
            this.getConfigsCached$(v.id).pipe(
              map(cfgs => {
                const patch = this.buildDisplaysPatch(v, cfgs, dicts);
                return { id: v.id, patch };
              }),
              catchError(() =>
                of({
                  id: v.id,
                  patch: { datasetsDisplay: [], spatialReferenceDisplay: null }
                })
              )
            ),
            6 //6 at the same time
          )
        );

        //    - first baseRows
        //    - update row with patches
        return merge(
          of({ rows: baseRows, total }),
          patches$.pipe(
            scan((state, { id, patch }) => {
              const idx = state.rows.findIndex((r: any) => r.id === id);
              if (idx === -1) return state;

              const updatedRow = { ...state.rows[idx], ...patch };
              const newRows = state.rows.slice();
              newRows[idx] = updatedRow;

              return { rows: newRows, total: state.total };
            }, { rows: baseRows, total })
          )
        );
      }),
      catchError(err => {
        console.error('Facade Error:', err);
        this.loadingSubject.next(false);
        return of({ rows: [], total: 0 });
      }),
      finalize(() => this.loadingSubject.next(false))
    );
  }

  private buildDisplaysPatch(validation: any, configs: any[], dicts: Dictionaries): {
    datasetsDisplay: any[];
    spatialReferenceDisplay: any | null;
  } {
    const resolveName = (cfg: any) => {
      const ds = dicts.datasets.get(cfg.dataset);
      const ver = dicts.versions.get(cfg.version);
      const vr = dicts.variables.get(cfg.variable);

      return {
        dataset: ds?.pretty_name || ds?.short_name || `ID: ${cfg.dataset}`,
        version: ver?.pretty_name || ver?.short_name || `ID: ${cfg.version}`,
        variable: vr?.pretty_name || vr?.short_name || `ID: ${cfg.variable}`,
        unit: vr?.unit || ''
      };
    };

    const datasetsDisplay = (configs || []).map(c => resolveName(c));
    const spatialCfg = (configs || []).find(c => c.is_spatial_reference);
    const spatialReferenceDisplay = spatialCfg ? resolveName(spatialCfg) : null;

    return { datasetsDisplay, spatialReferenceDisplay };
  }

  /**
 * Utility to convert component UI state (filters, pagination, sorting) 
 * into HttpParams for the backend API.
 */
  ValidationRunFilters(f: any, p: any, s: any): HttpParams {
  let params = new HttpParams()
    .set('offset', String(p.page * p.rows))
    .set('limit', String(p.rows));

    // Sorting logic
    const sortKey = s.field === 'name_tag' ? 'name' : s.field;
    params = params.set('order', s.order === 1 ? `${sortKey}:asc` : `${sortKey}:desc`);

    // Text filters
    if (f.name?.trim()) params = params.set('filter:name', f.name.trim());
    if (f.dataset?.trim()) params = params.set('filter:dataset', f.dataset.trim());

    // Date range logic
    if (f.dateRange?.[0] && f.dateRange?.[1]) {
      const from = f.dateRange[0].toISOString().split('T')[0];
      const to = f.dateRange[1].toISOString().split('T')[0];
      params = params.set('filter:start_time', `${from},${to}`);
    }

    return params;
  }

  /**
   * Toggles the "pinned" (tracked) status of a validation run.
   * @param id - Validation Run ID
   * @param isPinned - Current tracking state
   */

  togglePin(id: string, isPinned: boolean): Observable<any> {
    return isPinned 
      ? this.validationService.removeValidation(id) 
      : this.validationService.addValidation(id);
  }

  /**
   * Clears the configuration cache to force fresh data fetching on next load.
   */
  clearCache(): void {
    this.configCache.clear();
  }
}
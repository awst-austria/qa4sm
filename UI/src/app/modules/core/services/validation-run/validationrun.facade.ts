import { Injectable, inject } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import { BehaviorSubject, combineLatest, forkJoin, of, Observable } from 'rxjs';
import { map, switchMap, catchError, shareReplay, finalize, tap } from 'rxjs/operators';

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
    shareReplay(1) 
  );

  /**
   * Fetches validation runs and enriches them with full dataset/version/variable names.
   * Handles pagination, filtering, and caching automatically.
   * * @param mode - Source of validations: 'published' or 'user' (My Validations)
   * * @param params - HttpParams containing filters, sorting, and pagination
   */
  getValidations(mode: 'published' | 'user', params: HttpParams): Observable<{rows: any[], total: number}> {
    this.loadingSubject.next(true);

    const apiCall$ = mode === 'published' 
      ? this.validationService.getPublishedValidationruns(params)
      : this.validationService.getMyValidationruns(params);

    return combineLatest([this.dictionaries$, apiCall$]).pipe(
      switchMap(([dicts, response]) => {
        if (!response.validations?.length) {
          return of({ rows: [], total: 0 });
        }

        /** * For each validation, we create a sub-stream to fetch its configurations.
         * If the data is already in cache, we skip the network request.
         */
        const enrichmentRequests = response.validations.map(v => {
          if (this.configCache.has(v.id)) {
            const cachedConfigs = this.configCache.get(v.id)!;
            return of(this.enrichValidationData(v, cachedConfigs, dicts));
          }

          return this.datasetConfigService.getConfigByValidationrun(v.id).pipe(
            tap(configs => this.configCache.set(v.id, configs)),
            map(configs => this.enrichValidationData(v, configs, dicts)),
            catchError(() => of({ ...v, datasetsDisplay: [] })) // Если один запрос упал, не рушим всё
          );
        });

        return forkJoin(enrichmentRequests).pipe(
          map(enrichedRows => ({
            rows: enrichedRows,
            total: response.length
          }))
        );
      }),
      catchError(err => {
        console.error('Facade Error:', err);
        return of({ rows: [], total: 0 });
      }),
      finalize(() => this.loadingSubject.next(false))
    );
  }

  /**
   * Transforms raw IDs into human-readable display objects.
   * Attaches 'datasetsDisplay' property to the validation object.
   * * @param validation - The raw validation run object from API
   * * @param configs - Dataset configurations linked to this run
   * * @param dicts - Metadata dictionaries for ID-to-Name resolution
   */
  private enrichValidationData(validation: any, configs: any[], dicts: Dictionaries) {
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

    // Pre-calculated fields for direct binding in HTML templates
    validation.datasetsDisplay = (configs || []).map(c => resolveName(c));
    
    const spatialCfg = (configs || []).find(c => c.is_spatial_reference);
    validation.spatialReferenceDisplay = spatialCfg ? resolveName(spatialCfg) : null;

    return validation;
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
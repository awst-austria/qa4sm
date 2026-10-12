import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DatasetService } from '../../../core/services/dataset/dataset.service';
import { DatasetDto } from '../../../core/services/dataset/dataset.dto';

import { combineLatest, Observable, of } from 'rxjs';
import { DatasetVersionDto } from '../../../core/services/dataset/dataset-version.dto';
import { DatasetVersionService } from '../../../core/services/dataset/dataset-version.service';
import { DatasetComponentSelectionModel } from './dataset-component-selection-model';
import { DatasetVariableDto } from '../../../core/services/dataset/dataset-variable.dto';
import { DatasetVariableService } from '../../../core/services/dataset/dataset-variable.service';
import { catchError, map, shareReplay, switchMap, tap } from 'rxjs/operators';
import { ValidationRunConfigService } from '../../../../pages/validate/service/validation-run-config.service';
import { AuthService } from '../../../core/services/auth/auth.service';

@Component({
    selector: 'qa-dataset',
    templateUrl: './dataset.component.html',
    styleUrls: ['./dataset.component.scss'],
    standalone: false
})
export class DatasetComponent implements OnInit {

  datasets$: Observable<DatasetDto[]>;

  groupedDatasets: { label: string; icon: string; items: DatasetDto[] }[] = [];

  selectableDatasetVersions$: Observable<DatasetVersionDto[]>;
  selectableDatasetVariables$: Observable<DatasetVariableDto[]>;

  selectableDatasetVersionsObserver = {
    next: (versions: DatasetVersionDto[]) => this.onSelectableVersionsNext(versions),
    complete: () => this.onSelectableVersionsComplete()
  }

  selectableDatasetVariablesObserver = {
    next: (variables: DatasetVariableDto[]) => this.onSelectableVariablesNext(variables),
    complete: () => this.onSelectableVariablesComplete()
  }

  @Input() selectionModel: DatasetComponentSelectionModel;
  @Input() removable = false;
  @Output() changeDataset = new EventEmitter<DatasetComponentSelectionModel>();


  datasetSelectorId: string;
  versionSelectorId: string;
  variableSelectorId: string;
  newerVersionExists = false;
  newestVersionId: number;


  constructor(private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private validationConfigService: ValidationRunConfigService,
              public authService: AuthService) {
  }

  ngOnInit(): void {

    // Re-fetched on every auth change: the server returns a different set
    // depending on who is asking. shareReplay keeps it to one request per
    // component instance rather than one per emission downstream.
    const allDatasets$ = this.authService.currentUserResolved$.pipe(
      switchMap(() => this.datasetService.getAllDatasets(true)),
      catchError(() => of([] as DatasetDto[])),
      shareReplay(1)
    );

    // The visible dataset list depends both on which datasets are already selected
    // (ISMN can only be picked once) and on who is logged in, so both sources are
    // combined here. currentUserResolved$ only emits once the session check is done,
    // which keeps the grouping from being built against an unknown user.
    this.datasets$ = combineLatest([
      allDatasets$,
      this.validationConfigService.listOfSelectedConfigs,
      this.authService.currentUserResolved$
    ]).pipe(
      map(([all, configs, user]) => {
        const hasISMN = configs.some(c => c.datasetModel.selectedDataset?.short_name === 'ISMN');
        const currentIsISMN = this.selectionModel.selectedDataset?.short_name === 'ISMN';

        const datasets = (hasISMN && !currentIsISMN)
          ? all.filter(d => d.pretty_name !== 'ISMN')
          : all;

        return { datasets, userId: user?.id ?? null };
      }),
      tap(({ datasets, userId }) => this.buildGroupedDatasets(datasets, userId)),
      map(({ datasets }) => datasets)
    );

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id).pipe(
      tap(datasetVersions => this.checkIfNewerVersionExists(datasetVersions))
    );

    this.selectableDatasetVariables$ = this.datasetVariableService.getVariablesByVersion(this.selectionModel.selectedVersion.id);

    this.setSelectorsId();

  }

   updateSelectableVersionsAndVariableAndEmmit(): void {
    if (!this.selectionModel.selectedDataset?.versions?.length) {
      return;
    }

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id).pipe(
      tap(versions => this.checkIfNewerVersionExists(versions))
    );


    this.selectableDatasetVersions$.subscribe(this.selectableDatasetVersionsObserver);
    this.setSelectorsId();
  }

  private buildGroupedDatasets(datasets: DatasetDto[], currentUserId: number | null): void {
    const platform: DatasetDto[] = [];
    const user: DatasetDto[] = [];
    const shared: DatasetDto[] = [];

    for (const d of datasets) {
      const ownerId = d.user ?? null;

      if (ownerId === null) {
        platform.push(d);
      } else if (currentUserId !== null && ownerId === currentUserId) {
        user.push(d);
      } else if (d.is_shared > 0) {
        shared.push(d);
      }
    }

    this.groupedDatasets = [
      platform.length ? { label: 'Platform datasets', icon: 'pi pi-database',  items: platform } : null,
      user.length     ? { label: 'User datasets',     icon: 'pi pi-user',      items: user }     : null,
      shared.length   ? { label: 'Shared datasets',   icon: 'pi pi-share-alt', items: shared }   : null,
    ].filter(Boolean);
  }

  private onSelectableVersionsNext(versions): void {
    this.selectionModel.selectedVersion = versions[0];
  }

  private onSelectableVersionsComplete(): void {
    this.selectableDatasetVariables$ = this.datasetVariableService
      .getVariablesByVersion(this.selectionModel.selectedVersion.id);

    this.selectableDatasetVariables$.subscribe(this.selectableDatasetVariablesObserver);
    this.setSelectorsId();
  }

  private onSelectableVariablesNext(variables): void {
    this.selectionModel.selectedVariable = variables[0];
  }

  private onSelectableVariablesComplete(): void {
    this.changeDataset.emit(this.selectionModel);
    this.setSelectorsId();
  }

  onVersionChange(versions: DatasetVersionDto[]): void {
    this.checkIfNewerVersionExists(versions);
    this.changeDataset.emit(this.selectionModel);
  }

  checkIfNewerVersionExists(versions: DatasetVersionDto[]): void {
    if (!versions?.length) {
      this.newerVersionExists = false;
      return;
    }
    const maxId = Math.max(...versions.map(version => version.id));
    this.newerVersionExists = maxId > this.selectionModel.selectedVersion?.id;
    this.newestVersionId = maxId;
  }

  setSelectorsId(): void {
    const datasetIdentifier = `${this.selectionModel.selectedDataset?.id}_${this.selectionModel.selectedVersion?.id}_${this.selectionModel.selectedVariable?.id}`;
    this.datasetSelectorId = 'dataset_' + datasetIdentifier;
    this.versionSelectorId = 'version_' + datasetIdentifier;
    this.variableSelectorId = 'variable_' + datasetIdentifier;
  }
}
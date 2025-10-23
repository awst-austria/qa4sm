import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DatasetService } from '../../../core/services/dataset/dataset.service';
import { DatasetDto } from '../../../core/services/dataset/dataset.dto';

import { Observable } from 'rxjs';
import { DatasetVersionDto } from '../../../core/services/dataset/dataset-version.dto';
import { DatasetVersionService } from '../../../core/services/dataset/dataset-version.service';
import { DatasetComponentSelectionModel } from './dataset-component-selection-model';
import { DatasetVariableDto } from '../../../core/services/dataset/dataset-variable.dto';
import { DatasetVariableService } from '../../../core/services/dataset/dataset-variable.service';
import { map, tap } from 'rxjs/operators';
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
  allDatasets$: Observable<DatasetDto[]>;

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

    this.allDatasets$ = this.datasetService.getAllDatasets(true);

    this.validationConfigService.listOfSelectedConfigs.subscribe(configs => {
    const hasISMN = configs.some(c => c.datasetModel.selectedDataset?.short_name === 'ISMN');
    const currentIsISMN = this.selectionModel.selectedDataset?.short_name === 'ISMN';

    if (hasISMN && !currentIsISMN) {
    // ISMN is already selected somewhere else, and the current card is not ISMN -> hide ISMN.
    this.datasets$ = this.allDatasets$.pipe(
      map(datasets => datasets.filter(d => d.pretty_name !== 'ISMN'))
    );
    } else {
    // No restrictions on user/non-user — all user datasets can be selected.
    this.datasets$ = this.allDatasets$;
    }
    });

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id).pipe(
      tap(datasetVersions => this.checkIfNewerVersionExists(datasetVersions))
    );

    this.selectableDatasetVariables$ = this.datasetVariableService.getVariablesByVersion(this.selectionModel.selectedVersion.id);

    this.setSelectorsId();
  }

   updateSelectableVersionsAndVariableAndEmmit(): void {
    if (this.selectionModel.selectedDataset === undefined || this.selectionModel.selectedDataset.versions.length === 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id).pipe(
      tap(versions => this.checkIfNewerVersionExists(versions))
    );


    this.selectableDatasetVersions$.subscribe(this.selectableDatasetVersionsObserver);
    this.setSelectorsId();
  }

  private onSelectableVersionsNext(versions): void {
    this.selectionModel.selectedVersion = versions[0];
  }

  private onSelectableVersionsComplete(): void {
    this.selectableDatasetVariables$ = this.datasetVariableService.getVariablesByVersion(this.selectionModel.selectedVersion.id);

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
    this.newerVersionExists = Math.max(...versions.map(version => version.id)) > this.selectionModel.selectedVersion.id
    this.newestVersionId = Math.max(...versions.map(version => version.id));
  }

  setSelectorsId(): void {
    const datasetIdentifier = `${this.selectionModel.selectedDataset?.id}_
    ${this.selectionModel.selectedVersion?.id}_ ${this.selectionModel.selectedVariable?.id}`
    this.datasetSelectorId = 'dataset_' + datasetIdentifier;
    this.versionSelectorId = 'version_' + datasetIdentifier;
    this.variableSelectorId = 'variable_' + datasetIdentifier;
  }
}

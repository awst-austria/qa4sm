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
  styleUrls: ['./dataset.component.scss']
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
    this.allDatasets$ = this.datasetService.getDatasetsWithOkUserStatus();

    this.validationConfigService.listOfSelectedConfigs.subscribe(configs => {
      if (configs.filter(config => config.datasetModel.selectedDataset?.short_name === 'ISMN').length !== 0
        && this.selectionModel.selectedDataset?.short_name !== 'ISMN') {
        this.datasets$ = this.allDatasets$
          .pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
            return datasets.filter(dataset => dataset.pretty_name !== 'ISMN');
          }));
      } else if (configs.filter(config => config.datasetModel.selectedDataset?.user).length == configs.length - 1 && !this.selectionModel.selectedDataset?.user) {
        this.datasets$ = this.allDatasets$
          .pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
            return datasets.filter(dataset => !dataset.user);
          }));
      } else {
        this.datasets$ = this.allDatasets$
          .pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
            return datasets;
          }));
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

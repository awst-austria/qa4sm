import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';

import {Observable} from 'rxjs';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetComponentSelectionModel} from './dataset-component-selection-model';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {map} from 'rxjs/operators';
import {ValidationRunConfigService} from '../../../../pages/validate/service/validation-run-config.service';
import {AuthService} from '../../../core/services/auth/auth.service';


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
    next: versions => this.onSelectableVersionsNext(versions),
    complete: () => this.onSelectableVersionsComplete()
  }

  selectableDatasetVariablesObserver = {
    next: variables => this.onSelectableVariablesNext(variables),
    complete: () => this.onSelectableVariablesComplete()
  }

  @Input() selectionModel: DatasetComponentSelectionModel;
  @Input() removable = false;
  @Output() changeDataset = new EventEmitter<DatasetComponentSelectionModel>();

  datasetSelectorId: string;
  versionSelectorId: string;
  variableSelectorId: string;

  constructor(private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private validationConfigService: ValidationRunConfigService,
              public authService: AuthService) {
  }


  ngOnInit(): void {
    this.allDatasets$ = this.datasetService.getAllDatasets(true)

    this.validationConfigService.listOfSelectedConfigs.subscribe(configs => {
      if (configs.filter(config => config.datasetModel.selectedDataset?.short_name === 'ISMN').length !== 0
        && this.selectionModel.selectedDataset?.short_name !== 'ISMN') {
        this.datasets$ = this.allDatasets$
          .pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
            return this.sortById(datasets.filter(dataset => dataset.pretty_name !== 'ISMN'));
          }));
      } else if (configs.filter(config => config.datasetModel.selectedDataset?.user).length == configs.length - 1 && !this.selectionModel.selectedDataset?.user) {
        this.datasets$ = this.allDatasets$
          .pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
            return this.sortById(datasets.filter(dataset => !dataset.user));
          }));
      } else {
        this.datasets$ = this.allDatasets$
          .pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
            return this.sortById(datasets);
          }));
      }
    });


    this.selectableDatasetVersions$ = this.sortObservableById(
      this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id));

    this.selectableDatasetVariables$ = this.sortObservableById(
      this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id));

    this.setSelectorsId();
  }

  private updateSelectableVersionsAndVariableAndEmmit(): void {
    if (this.selectionModel.selectedDataset === undefined || this.selectionModel.selectedDataset.versions.length === 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.sortObservableById(
      this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id));


    this.selectableDatasetVersions$.subscribe(this.selectableDatasetVersionsObserver);
    this.setSelectorsId();
  }

  private onSelectableVersionsNext(versions): void {
    this.selectionModel.selectedVersion = versions[0];
  }

  private onSelectableVersionsComplete(): void {
    this.selectableDatasetVariables$ = this.sortObservableById(
      this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id));

    this.selectableDatasetVariables$.subscribe(this.selectableDatasetVariablesObserver)
    this.setSelectorsId();
  }

  private onSelectableVariablesNext(variables): void {
    this.selectionModel.selectedVariable = variables[variables.length - 1];
  }

  private onSelectableVariablesComplete(): void {
    this.changeDataset.emit(this.selectionModel);
    this.setSelectorsId();
  }

  onDatasetChange(): void {
    this.updateSelectableVersionsAndVariableAndEmmit();
  }

  onVersionChange(): void {
    this.changeDataset.emit(this.selectionModel);
  }

  sortById(listOfElements): any {
    return listOfElements.sort((a, b) => {
      return a.id < b.id ? 1 : -1;
    });
  }

  sortObservableById(observableOfListOfElements: Observable<any>): Observable<any> {
    return observableOfListOfElements.pipe(map((data) => {
      data.sort((a, b) => {
        return a.id < b.id ? 1 : -1;
      });
      return data;
    }));
  }

  setSelectorsId(): void {
    const datasetIdentifier = `${this.selectionModel.selectedDataset?.id}_
    ${this.selectionModel.selectedVersion?.id}_ ${this.selectionModel.selectedVariable?.id}`
    this.datasetSelectorId = 'dataset_' + datasetIdentifier;
    this.versionSelectorId = 'version_' + datasetIdentifier;
    this.variableSelectorId = 'variable_' + datasetIdentifier;
  }
}

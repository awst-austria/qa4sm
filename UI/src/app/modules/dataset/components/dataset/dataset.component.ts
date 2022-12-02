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

  @Input() selectionModel: DatasetComponentSelectionModel;
  @Input() removable = false;
  @Output() changeDataset = new EventEmitter<DatasetComponentSelectionModel>();


  constructor(private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private validationConfigService: ValidationRunConfigService) {
  }


  ngOnInit(): void {
    this.allDatasets$ = this.datasetService.getAllDatasets(false);

    this.validationConfigService.listOfSelectedConfigs.subscribe(configs => {
      if (configs.filter(config => config.datasetModel.selectedDataset?.short_name === 'ISMN').length !== 0
        && this.selectionModel.selectedDataset?.short_name !== 'ISMN'){
        this.datasets$ = this.allDatasets$.pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
          return this.sortById(datasets.filter(dataset => dataset.pretty_name !== 'ISMN'));
        }));
      } else {
        this.datasets$ = this.allDatasets$.pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
          return this.sortById(datasets);
        }));
      }
    });

    this.selectableDatasetVersions$ = this.sortObservableById(
      this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id));

    this.selectableDatasetVariables$ = this.sortObservableById(
      this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id));
  }

  private updateSelectableVersionsAndVariableAndEmmit(): void {
    if (this.selectionModel.selectedDataset === undefined || this.selectionModel.selectedDataset.versions.length === 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.sortObservableById(
      this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id));


    this.selectableDatasetVersions$.subscribe(
      versions => {
        this.selectionModel.selectedVersion = versions[0];
      },
      () => {
      },
      () => {
        this.selectableDatasetVariables$ = this.sortObservableById(
          this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id));

        this.selectableDatasetVariables$.subscribe(
          variables => {
            this.selectionModel.selectedVariable = variables[0];
          },
          () => {},
          () => {
            this.changeDataset.emit(this.selectionModel);
          });
      });
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
}

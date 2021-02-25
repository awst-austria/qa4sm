import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {DatasetService} from '../../services/dataset.service';
import {DatasetDto} from '../../services/dataset.dto';

import {Observable} from 'rxjs';
import {DatasetVersionDto} from '../../services/dataset-version.dto';
import {DatasetVersionService} from '../../services/dataset-version.service';
import {DatasetComponentSelectionModel} from './dataset-component-selection-model';
import {DatasetVariableDto} from '../../services/dataset-variable.dto';
import {DatasetVariableService} from '../../services/dataset-variable.service';


@Component({
  selector: 'qa-dataset',
  templateUrl: './dataset.component.html',
  styleUrls: ['./dataset.component.scss']
})
export class DatasetComponent implements OnInit {

  datasets$: Observable<DatasetDto[]>;

  selectableDatasetVersions$: Observable<DatasetVersionDto[]>;
  selectableDatasetVariables$: Observable<DatasetVariableDto[]>;

  @Input() selectionModel: DatasetComponentSelectionModel;
  @Input() removable: boolean = false;
  @Output() changeDataset = new EventEmitter<DatasetComponentSelectionModel>();


  constructor(private datasetService: DatasetService, private datasetVersionService: DatasetVersionService, private datasetVariableService: DatasetVariableService) {
  }

  ngOnInit(): void {

    this.datasets$ = this.datasetService.getAllDatasets();
    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id);
    this.selectableDatasetVariables$ = this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id);
  }

  private updateSelectableVersionsAndVariable() {
    if (this.selectionModel.selectedDataset == undefined || this.selectionModel.selectedDataset.versions.length == 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id);
    this.selectableDatasetVersions$.subscribe(versions => {
      this.selectionModel.selectedVersion = versions[0];
    });

    this.selectableDatasetVariables$ = this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id);
    this.selectableDatasetVariables$.subscribe(variables => {
      this.selectionModel.selectedVariable = variables[0];
    });
  }

  onDatasetChange() {
    this.updateSelectableVersionsAndVariable();
    this.changeDataset.emit(this.selectionModel);
  }
}

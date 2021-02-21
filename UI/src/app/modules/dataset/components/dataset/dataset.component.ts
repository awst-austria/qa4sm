import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {DatasetService} from '../../services/dataset.service';
import {DatasetDto} from '../../services/dataset.dto';

import {Observable} from 'rxjs';
import {DatasetVersionDto} from '../../services/dataset-version.dto';
import {DatasetVersionService} from '../../services/dataset-version.service';
import {DatasetComponentSelectionModel} from './dataset-component-selection-model';


@Component({
  selector: 'qa-dataset',
  templateUrl: './dataset.component.html',
  styleUrls: ['./dataset.component.scss']
})
export class DatasetComponent implements OnInit {

  datasets: DatasetDto[] = [];
  datasets$: Observable<DatasetDto[]>;
  datasetVersions: DatasetVersionDto[] = [];  //All dataset versions
  selectableDatasetVersions: DatasetVersionDto[]; //Dataset versions that belong to the selected dataset
  selectableDatasetVersions$: Observable<DatasetVersionDto[]>;

  @Input() selectionModel: DatasetComponentSelectionModel;
  @Input() removable: boolean = false;
  @Output() removeDataset = new EventEmitter<DatasetComponentSelectionModel>();


  constructor(private datasetService: DatasetService, private datasetVersionService: DatasetVersionService) {
  }

  ngOnInit(): void {
    //load datasets
    this.datasets$ = this.datasetService.getAllDatasets();

  }

  private updateSelectableVersionsAndVariable() {
    if (this.selectionModel.selectedDataset == undefined || this.selectionModel.selectedDataset.versions.length == 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id);
    this.selectableDatasetVersions$.subscribe(versions => {
      this.selectionModel.selectedVersion = versions[0];
    });
  }

  onDatasetChange() {
    this.updateSelectableVersionsAndVariable();
  }

  onRemoveDataset() {
    this.removeDataset.emit(this.selectionModel);
  }


}

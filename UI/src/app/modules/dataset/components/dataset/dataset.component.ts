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
  @Input() reference: boolean = false;
  @Output() changeDataset = new EventEmitter<DatasetComponentSelectionModel>();


  constructor(private datasetService: DatasetService, private datasetVersionService: DatasetVersionService, private datasetVariableService: DatasetVariableService) {
  }

  ngOnInit(): void {

    //Create dataset observable
    if (this.reference) {
      this.datasets$ = this.datasetService.getAllDatasets();
    } else {
      //filter out datasets than can be used only as reference
      this.datasets$ = this.datasetService.getAllDatasets().pipe(map<DatasetDto[], DatasetDto[]>(datasets => {
        let nonReferenceDatasets: DatasetDto[] = [];
        datasets.forEach(dataset => {
          if (dataset.is_only_reference == false) {
            nonReferenceDatasets.push(dataset);
          }
        });
        return nonReferenceDatasets;
      }));
    }


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

  private updateSelectableVersionsAndVariableAndEmmit(): void{
    if (this.selectionModel.selectedDataset === undefined || this.selectionModel.selectedDataset.versions.length == 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectionModel.selectedDataset.id);
    this.selectableDatasetVersions$.subscribe(versions => {
        this.selectionModel.selectedVersion = versions[0];
      },
      () => {},
      () => {
        this.selectableDatasetVariables$ = this.datasetVariableService.getVariablesByDataset(this.selectionModel.selectedDataset.id);
        this.selectableDatasetVariables$.subscribe(variables => {
            this.selectionModel.selectedVariable = variables[0];
          },
          () => {},
          () => this.changeDataset.emit(this.selectionModel));
      });
  }

  onDatasetChange(): void{
    this.updateSelectableVersionsAndVariableAndEmmit();
  }
  onVersionChange(): void{
    this.changeDataset.emit(this.selectionModel);
  }
}

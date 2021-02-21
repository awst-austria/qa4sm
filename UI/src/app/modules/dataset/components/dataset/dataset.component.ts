import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {DatasetService} from '../../services/dataset.service';
import {DatasetDto} from '../../services/dataset.dto';
import {DatasetSelection} from './dataset-selection';
import {Observable} from 'rxjs';
import {DatasetVersionDto} from '../../services/dataset-version.dto';
import {DatasetVersionService} from '../../services/dataset-version.service';
import {filter} from 'rxjs/operators';


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

  @Input() datasetSelection: DatasetSelection;
  @Input() removable: boolean = false;
  @Output() removeDataset = new EventEmitter<DatasetSelection>();

  selectedDataset: DatasetDto;
  selectedDatasetVersion: DatasetVersionDto;


  constructor(private datasetService: DatasetService, private datasetVersionService: DatasetVersionService) {
  }

  ngOnInit(): void {
    //load datasets
    this.datasets$ = this.datasetService.getAllDatasets();
    this.datasetService.getAllDatasets().subscribe(
      datasets => {
        if (this.datasetSelection != undefined) {
          this.selectedDataset = datasets[0];
          this.updateSelectableVersionsAndVariable();
        } else {
          console.error('dataset selection is undefined');
        }
      }
    );
  }

  private updateSelectableVersionsAndVariable() {
    if (this.selectedDataset == undefined || this.selectedDataset.versions.length == 0) {
      return;
    }

    this.selectableDatasetVersions$ = this.datasetVersionService.getVersionsByDataset(this.selectedDataset.id);
    this.selectableDatasetVersions$.subscribe(data => {
      this.selectedDatasetVersion = data[0];
      this.updateSelection();
    });
  }

  onDatasetChange() {
    this.updateSelection();
    this.updateSelectableVersionsAndVariable();
  }

  private updateSelection() {
    this.datasetSelection.datasetId = this.selectedDataset.id;
    this.datasetSelection.datasetName = this.selectedDataset.pretty_name;
  }

  onRemoveDataset() {
    this.removeDataset.emit(this.datasetSelection);
  }


}

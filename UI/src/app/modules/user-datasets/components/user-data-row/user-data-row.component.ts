import {Component, Input, OnInit} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {BehaviorSubject, Observable} from 'rxjs';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';

@Component({
  selector: 'qa-user-data-row',
  templateUrl: './user-data-row.component.html',
  styleUrls: ['./user-data-row.component.scss']
})
export class UserDataRowComponent implements OnInit {

  @Input() userDataset: UserDataFileDto;
  variableName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  latitudeName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  longitudeName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  timeName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  variableFieldName = 'variable_name';
  latFieldName = 'lat_name';
  lonFieldName = 'lon_name';
  timeFiledName = 'time_name';
  editVariable = {opened: false};
  editLatName = {opened: false};
  editLonName = {opened: false};
  editTimeName = {opened: false};

  // variables$: Observable<DatasetVariableDto>[] = [];

  constructor(private userDatasetService: UserDatasetsService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.datasetVariableService.getVariableById(this.userDataset.variable).subscribe(variableData => {
      this.variableName$.next(variableData.short_name);
    });
    this.latitudeName$.next(
      this.userDataset.latname ? this.userDataset.latname : '**choose**'
    );
    this.longitudeName$.next(
      this.userDataset.lonname ? this.userDataset.lonname : '**choose**'
    );
    this.timeName$.next(
      this.userDataset.timename ? this.userDataset.timename : '**choose**'
    );
  }

  removeDataset(dataFileId: string): void {
    if (!confirm('Do you really want to delete the dataset?')) {
      return;
    }
    this.userDatasetService.deleteUserData(dataFileId).subscribe(() => {
      this.userDatasetService.refresh.next(true);
    });
  }

  getDataset(datasetId): Observable<DatasetDto> {
    return this.datasetService.getDatasetById(datasetId);
  }

  getDatasetVersion(versionId): Observable<DatasetVersionDto> {
    return this.datasetVersionService.getVersionById(versionId);
  }

  getDatasetVariable(variableId): Observable<DatasetVariableDto> {
    return this.datasetVariableService.getVariableById(variableId);
  }

  testDataset(dataFileId): void {
    this.userDatasetService.testDataset(dataFileId).subscribe(data => {
      console.log(data);
    });
  }

  updateMetadata(fieldName, fieldValue, userDataId): void {
    this.userDatasetService.updateMetadata(fieldName, fieldValue, userDataId).subscribe(() => {
        this.toggle(fieldName, false);
        if (fieldName === this.variableFieldName) {
          this.variableName$.next(fieldValue);
        }
        if (fieldName === this.latFieldName) {
          this.latitudeName$.next(fieldValue);
        }
        if (fieldName === this.lonFieldName) {
          this.longitudeName$.next(fieldValue);
        }
        if (fieldName === this.timeFiledName) {
          this.timeName$.next(fieldValue);
        }
      },
      () => {
      },
      () => {
        this.toastService.showSuccess('Metadata has been updated');
      });
  }

  toggle(fieldName, open): void {
    let editableField;
    switch (fieldName) {
      case this.variableFieldName:
        editableField = this.editVariable;
        break;
      case this.lonFieldName:
        editableField = this.editLonName;
        break;
      case this.latFieldName:
        editableField = this.editLatName;
        break;
      case this.timeFiledName:
        editableField = this.editTimeName;
        break;
    }
    editableField.opened = open;
  }
}

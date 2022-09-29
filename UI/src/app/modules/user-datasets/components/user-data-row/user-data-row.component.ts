import {Component, Input, OnInit} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {BehaviorSubject, Observable} from 'rxjs';
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
  datasetName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  versionName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  variableName: { shortName$: BehaviorSubject<string>, prettyName$: BehaviorSubject<string> } =
    {shortName$: new BehaviorSubject<string>(''), prettyName$: new BehaviorSubject<string>('')};
  latitudeName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  longitudeName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  timeName$: BehaviorSubject<string> = new BehaviorSubject<string>('');

  datasetFieldName = 'dataset_name';
  versionFieldName = 'version_name';
  variableFieldName = 'variable_name';
  latFieldName = 'lat_name';
  lonFieldName = 'lon_name';
  timeFiledName = 'time_name';

  editDataset = {opened: false};
  editVersion = {opened: false};
  editVariable = {opened: false};
  editLatName = {opened: false};
  editLonName = {opened: false};
  editTimeName = {opened: false};

  dateFormat = 'medium';
  timeZone = 'UTC';
  // variables$: Observable<DatasetVariableDto>[] = [];

  constructor(private userDatasetService: UserDatasetsService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.datasetService.getDatasetById(this.userDataset.dataset).subscribe(datasetData => {
      this.datasetName$.next(datasetData.pretty_name);
    });
    this.datasetVersionService.getVersionById(this.userDataset.version).subscribe(versionData => {
      this.versionName$.next(versionData.pretty_name);
    });
    this.datasetVariableService.getVariableById(this.userDataset.variable).subscribe(variableData => {
      this.variableName.shortName$.next(variableData.short_name);
      this.variableName.prettyName$.next(variableData.pretty_name);
    });
    this.latitudeName$.next(
      this.userDataset.lat_name ? this.userDataset.lat_name : '**choose**'
    );
    this.longitudeName$.next(
      this.userDataset.lon_name ? this.userDataset.lon_name : '**choose**'
    );
    this.timeName$.next(
      this.userDataset.time_name ? this.userDataset.time_name : '**choose**'
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

  updateMetadata(fieldName, fieldValue, userDataId): void {
    this.userDatasetService.updateMetadata(fieldName, fieldValue, userDataId).subscribe(() => {
        this.toggle(fieldName, false);
        if (fieldName === this.datasetFieldName){
          this.datasetName$.next(fieldValue);
        }
        if (fieldName === this.versionFieldName){
          this.versionName$.next(fieldValue);
        }
        if (fieldName === this.variableFieldName) {
          this.variableName.prettyName$.next(
            this.userDataset.all_variables.find(choice => choice.name === fieldValue).long_name);
          this.variableName.shortName$.next(fieldValue);
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
        this.toastService.showError('Metadata could not be updated');
      },
      () => {
        this.toastService.showSuccess('Metadata has been updated');
      });
  }

  toggle(fieldName, open): void {
    let editableField;
    switch (fieldName) {
      case this.datasetFieldName:
        editableField = this.editDataset;
        break;
      case this.versionFieldName:
        editableField = this.editVersion;
        break;
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

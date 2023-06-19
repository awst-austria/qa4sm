import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {BehaviorSubject, Observable} from 'rxjs';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {AuthService} from '../../../core/services/auth/auth.service';

@Component({
  selector: 'qa-user-data-row',
  templateUrl: './user-data-row.component.html',
  styleUrls: ['./user-data-row.component.scss']
})
export class UserDataRowComponent implements OnInit, OnDestroy {

  @Input() userDataset: UserDataFileDto;
  datasetName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  versionName$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  variableName: {
    shortName$: BehaviorSubject<string>,
    prettyName$: BehaviorSubject<string>,
    unit$: BehaviorSubject<string>
  } =
    {
      shortName$: new BehaviorSubject<string>(''),
      prettyName$: new BehaviorSubject<string>(''),
      unit$: new BehaviorSubject<string>('')
    };

  datasetFieldName = 'dataset_name';
  versionFieldName = 'version_name';
  variableFieldName = 'variable_name';

  editDataset = {opened: false};
  editVersion = {opened: false};
  editVariable = {opened: false};

  dateFormat = 'medium';
  timeZone = 'UTC';
  filePreprocessingStatus: any;
  getUserDataFileByIdObserver = {
    next: data => this.onGetUserDataFileByIdNext(data),
    error: () => this.onGetUserDataFileByIdError()
  }


  // variables$: Observable<DatasetVariableDto>[] = [];

  constructor(private userDatasetService: UserDatasetsService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private toastService: ToastService,
              public authService: AuthService) {
  }

  ngOnInit(): void {
    this.datasetService.getDatasetById(this.userDataset.dataset).subscribe(datasetData => {
      this.datasetName$.next(datasetData.pretty_name);
    });
    this.datasetVersionService.getVersionById(this.userDataset.version).subscribe(versionData => {
      this.versionName$.next(versionData.pretty_name);
    });
    this.updateVariable();
    this.refreshFilePreprocessingStatus();
  }

  removeDataset(dataFileId: string): void {
    if (!confirm('Do you really want to delete the dataset?')) {
      return;
    }
    this.userDatasetService.deleteUserData(dataFileId).subscribe(() => {
      this.userDatasetService.refresh.next(true);
      this.authService.init();
    });
  }

  updateVariable(): void {
    this.datasetVariableService.getVariableById(this.userDataset.variable, true).subscribe(variableData => {
      this.variableName.shortName$.next(variableData.short_name);
      this.variableName.prettyName$.next(variableData.pretty_name);
      this.variableName.unit$.next(variableData.unit);
    });
  }

  getDataset(datasetId): Observable<DatasetDto> {
    return this.datasetService.getDatasetById(datasetId);
  }

  getDatasetVersion(versionId): Observable<DatasetVersionDto> {
    return this.datasetVersionService.getVersionById(versionId);
  }

  updateMetadata(fieldName, fieldValue, userDataId): void {

    const updateMetadataObserver = {
      next: () => this.onUpdateMetadataNext(fieldName, fieldValue),
      error: () => this.onUpdateMetadataError(),
      complete: () => this.onUpdateMetadataComplete()
    }

    this.userDatasetService.updateMetadata(fieldName, fieldValue, userDataId).subscribe(updateMetadataObserver);
  }

  private onUpdateMetadataNext(fieldName, fieldValue): void{
    this.toggle(fieldName, false);
    if (fieldName === this.datasetFieldName) {
      this.datasetName$.next(fieldValue);
    }
    if (fieldName === this.versionFieldName) {
      this.versionName$.next(fieldValue);
    }
    if (fieldName === this.variableFieldName) {
      this.variableName.prettyName$.next(
        this.userDataset.all_variables.find(choice => choice.name === fieldValue).long_name);
      this.variableName.unit$.next(this.userDataset.all_variables.find(choice => choice.name === fieldValue).units);
      this.variableName.shortName$.next(fieldValue);
    }
  }

  private onUpdateMetadataError(): void{
    this.toastService.showError('Metadata could not be updated');
  }

  private onUpdateMetadataComplete(): void{
    this.toastService.showSuccess('Metadata has been updated');
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
    }
    editableField.opened = open;
  }

  getTheFileSize(): string {
    return this.userDatasetService.getTheSizeInProperUnits(this.userDataset.file_size);
  }


  refreshFilePreprocessingStatus(): void {
    if (!this.userDataset.metadata_submitted) {
      this.filePreprocessingStatus = setInterval(() => {
        this.userDatasetService.getUserDataFileById(this.userDataset.id).subscribe(this.getUserDataFileByIdObserver);
      }, 60 * 1000); // one minute
    }
  }

  private onGetUserDataFileByIdNext(data): void {
    if (data.metadata_submitted) {
      this.updateVariable();
      if (this.variableName.prettyName$.value !== 'none') {
        this.userDatasetService.refresh.next(true);
      }
    }
  }

  private onGetUserDataFileByIdError(): void{
    this.userDatasetService.refresh.next(true);
    this.toastService.showErrorWithHeader('File preprocessing failed',
      'File could not be preprocessed. Please make sure that you are uploading a proper file and if the ' +
      'file fulfills our requirements', 10000);
  }


  ngOnDestroy(): void {
    clearInterval(this.filePreprocessingStatus);
  }

}

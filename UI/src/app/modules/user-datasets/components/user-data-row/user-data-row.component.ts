import {Component, Input, OnDestroy, OnInit, signal} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {EMPTY, Observable} from 'rxjs';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {AuthService} from '../../../core/services/auth/auth.service';
import {DataManagementGroupsDto} from '../../services/data-management-groups.dto';
import {CustomHttpError} from '../../../core/services/global/http-error.service';
import {catchError} from 'rxjs/operators';

@Component({
    selector: 'qa-user-data-row',
    templateUrl: './user-data-row.component.html',
    styleUrls: ['./user-data-row.component.scss'],
    standalone: false
})
export class UserDataRowComponent implements OnInit, OnDestroy {

  @Input() userDataset: UserDataFileDto;
  @Input() dataManagementGroups: DataManagementGroupsDto[];
  // @Output() openShareDataWindow = new EventEmitter<any>()

  datasetGroups = signal<DataManagementGroupsDto[]>([])
  datasetName = signal('');
  versionName = signal('');

  variable = {
    shortName:  signal(''),
    prettyName: signal(''),
    unit: signal('')
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
    next: (data: any) => this.onGetUserDataFileByIdNext(data),
    error: () => this.onGetUserDataFileByIdError()
  }

  deleteDataObserver = {
    next: () => this.refreshAfterRemoval(),
    error: (error: CustomHttpError) => this.deleteUserDataError(error)
  }

  shareDataModalWindow = false;
  logWindowVisible: boolean = false;

  // groupToUpdate: DataManagementGroupsDto
  // variables$: Observable<DatasetVariableDto>[] = [];

  constructor(private userDatasetService: UserDatasetsService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService,
              private toastService: ToastService,
              public authService: AuthService) {
  }

  ngOnInit(): void {
    this.datasetGroups.set(this.dataManagementGroups.filter(group => this.userDataset.user_groups.includes(group.id)));
    this.datasetService.getDatasetById(this.userDataset.dataset)
      .pipe(catchError(() => this.fetchMetadataError('Dataset')))
      .subscribe(datasetData => {
        this.datasetName.set(datasetData.pretty_name);
      });
    this.datasetVersionService.getVersionById(this.userDataset.version)
      .pipe(catchError(() => this.fetchMetadataError('Version')))
      .subscribe(versionData => {
        this.versionName.set(versionData.pretty_name);
      });
    this.updateVariable();
    this.refreshFilePreprocessingStatus();
  }

  refreshAfterRemoval(): void {
    this.userDatasetService.refresh.next(true);
    this.authService.init();
  }

  removeDataset(dataset: UserDataFileDto): void {
    let warning = 'Do you really want to delete the dataset?'
    if (dataset.is_used_in_validation) {
      if (dataset.user_groups.length === 0) {
        warning += '\n\nPlease note that the data you are about to remove has been used in validations. ' +
          '\n\nIf you proceed the validations will become unreproducible.'
      } else {
        warning += '\n\nPlease note that the data you are about to remove has been used in validations and shared ' +
          'with other users. ' + '\n\nIf you proceed the validations will become unreproducible and other users will ' +
          'lose access to this dataset.'
      }
    } else if (dataset.user_groups.length !== 0) {
      warning += '\n\nPlease note that the data you are about to remove has been shared with other users. ' +
        '\n\nIf you proceed other users will lose access to this dataset.'
    }

    if (!confirm(warning)) {
      return;
    }

    if (this.userDataset.is_used_in_validation) {
      this.userDatasetService.deleteUserDataFileOnly(dataset.id)
        .subscribe(this.deleteDataObserver)
    } else {
      this.userDatasetService.deleteUserData(dataset.id)
        .subscribe(this.deleteDataObserver);
    }
  }

  deleteUserDataError(error: CustomHttpError): void {
    this.toastService.showErrorWithHeader(error.errorMessage.header,
      'We could not delete your file. Please try again later or contact our support team.')
  }


  updateVariable(): void {
    this.datasetVariableService.getVariableById(this.userDataset.variable, true)
      .pipe(catchError(() => this.fetchMetadataError('Variable')))
      .subscribe(variableData => {
        this.variable.shortName.set(variableData.short_name);
        this.variable.prettyName.set(variableData.pretty_name);
        this.variable.unit.set(variableData.unit);
      });
  }

  getDataset(datasetId): Observable<DatasetDto> {
    return this.datasetService.getDatasetById(datasetId);
  }

  getDatasetVersion(versionId): Observable<DatasetVersionDto> {
    return this.datasetVersionService.getVersionById(versionId);
  }

  updateMetadata(fieldName: string, fieldValue: string, userDataId: string): void {

    const updateMetadataObserver = {
      next: () => this.onUpdateMetadataNext(fieldName, fieldValue),
      error: () => this.onUpdateMetadataError(),
      complete: () => this.onUpdateMetadataComplete()
    }

    this.userDatasetService.updateMetadata(fieldName, fieldValue, userDataId).subscribe(updateMetadataObserver);
  }

  private onUpdateMetadataNext(fieldName, fieldValue): void {
    this.toggle(fieldName, false);
    if (fieldName === this.datasetFieldName) {
      this.datasetName.set(fieldValue);
    }
    if (fieldName === this.versionFieldName) {
      this.versionName.set(fieldValue);
    }
    if (fieldName === this.variableFieldName) {
      this.variable.prettyName.set(this.userDataset.all_variables.find(choice => choice.name === fieldValue).long_name);
      this.variable.unit.set(this.userDataset.all_variables.find(choice => choice.name === fieldValue).units);
      this.variable.shortName.set(fieldValue);
    }
  }

  private onUpdateMetadataError(): void {
    this.toastService.showError('Metadata could not be updated');
  }

  private onUpdateMetadataComplete(): void {
    this.toastService.showSuccess('Metadata has been updated');
  }

  toggle(fieldName: string, open: boolean): void {
    if (fieldName === this.datasetFieldName && this.datasetName()){
      this.editDataset.opened = open;
    } else if (fieldName === this.versionFieldName && this.versionName()) {
      this.editVersion.opened = open;
    } else if (fieldName === this.variableFieldName && this.variable.shortName()){
      this.editVariable.opened = open;
    }
  }

  getTheFileSize(): string {
    return this.userDatasetService.getTheSizeInProperUnits(this.userDataset.file_size);
  }

  // in th case when upload fails
  // get the value of UploadStatus
  getFileUploadStatus(): string {
    return this.userDataset.status;
  }
  // get the value of Error Message
  getFileUploadErrorMessage(): string {
   return this.userDataset.error_message || 'No errors';
  }
  // get the value of Log Information
  getFileUploadLogInfo(): string {
    return this.userDataset.log_info || 'No logs available';
  }

  showLogWindow() {
  this.logWindowVisible = true;
  }

  refreshFilePreprocessingStatus(): void {
    if (!this.userDataset.metadata_submitted) {
      this.filePreprocessingStatus = setInterval(() => {
        this.userDatasetService.getUserDataFileById(this.userDataset.id)
          .subscribe(this.getUserDataFileByIdObserver);
      }, 60 * 1000); // one minute
    }
  }

  private onGetUserDataFileByIdNext(data): void {
    if (data.metadata_submitted) {
      this.updateVariable();
      if (this.variable.prettyName() !== 'none'){
        this.userDatasetService.refresh.next(true);
      }
    }
  }

  private onGetUserDataFileByIdError(): void {
    this.userDatasetService.refresh.next(true);
    const errorMessage = 'File could not be preprocessed. ' +
      'Please make sure that you are uploading a proper file and if the file fulfills our requirements';
    const errorHeader = 'File preprocessing failed';

    this.toastService.showErrorWithHeader(errorHeader, errorMessage, 10000);
  }

  public openWindowForDataSharing(): void {
    this.shareDataModalWindow = true;
  }

  public manageSharingWindow(open): void {
    if (!open) {
      this.shareDataModalWindow = false;
      this.userDatasetService.getUserDataFileById(this.userDataset.id)
        .subscribe(data => {
          this.userDataset = data;
        }
      )
    }
  }

  fetchMetadataError(source: string): Observable<never> {
    this.toastService.showErrorWithHeader('Error fetching metadata',
      `${source} metadata could not be fetched, there might be information on your dataset missing. ` +
      'If the error persists, contact our support team.')
    return EMPTY
  }


  ngOnDestroy(): void {
    clearInterval(this.filePreprocessingStatus);
  }

}

import {Component, OnInit, signal} from '@angular/core';
import {UserDatasetsService} from '../../modules/user-datasets/services/user-datasets.service';
import {EMPTY, Observable} from 'rxjs';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {DataManagementGroupsDto} from '../../modules/user-datasets/services/data-management-groups.dto';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {catchError, tap} from 'rxjs/operators';
import {UserDataFileDto} from '../../modules/user-datasets/services/user-data-file.dto';
import {DatasetService} from '../../modules/core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../modules/core/services/dataset/dataset-version.service';
import {DatasetVariableService} from '../../modules/core/services/dataset/dataset-variable.service';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {CustomHttpError} from '../../modules/core/services/global/http-error.service';
import {CommonModule} from '@angular/common';
import {RouterLink} from '@angular/router';
import {TableModule} from 'primeng/table';
import {TagModule} from 'primeng/tag';
import {ButtonModule} from 'primeng/button';
import {DialogModule} from 'primeng/dialog';
import {TooltipModule} from 'primeng/tooltip';
import {InputTextModule} from 'primeng/inputtext';
import {SelectModule} from 'primeng/select';
import {FormsModule} from '@angular/forms';
import {ScrollTopModule} from 'primeng/scrolltop';
import {UserFileUploadComponent} from '../../modules/user-datasets/components/user-file-upload/user-file-upload.component';

interface DatasetMeta {
  datasetName: ReturnType<typeof signal<string>>;
  versionName: ReturnType<typeof signal<string>>;
  variable: {
    shortName: ReturnType<typeof signal<string>>;
    prettyName: ReturnType<typeof signal<string>>;
    unit: ReturnType<typeof signal<string>>;
  };
  editDataset: { opened: boolean };
  editVersion: { opened: boolean };
  editVariable: { opened: boolean };
  filePreprocessingStatus: any;
}

@Component({
  selector: 'qa-my-datasets',
  templateUrl: './my-datasets.component.html',
  styleUrls: ['./my-datasets.component.scss'],
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterLink,  
    TableModule, TagModule, ButtonModule, DialogModule,
    TooltipModule, InputTextModule, SelectModule, ScrollTopModule,
    UserFileUploadComponent]
})
export class MyDatasetsComponent implements OnInit {

  constructor(
    private userDatasetService: UserDatasetsService,
    public authService: AuthService,
    private settingsService: SettingsService,
    private datasetService: DatasetService,
    private datasetVersionService: DatasetVersionService,
    private datasetVariableService: DatasetVariableService,
    private toastService: ToastService,
  ) {}

  dataManagementGroups$: Observable<DataManagementGroupsDto[]>;
  readMore = false;
  hasNoSpaceLimit: boolean;
  hasNoSpaceAssigned: boolean;
  maintenanceMode = false;
  datasetFetchError = false;
  settingsError = false;

  metaMap = new Map<string, DatasetMeta>();

  datasetFieldName = 'dataset_name';
  versionFieldName = 'version_name';
  variableFieldName = 'variable_name';

  logWindowVisible = false;
  logTarget: UserDataFileDto | null = null;

  confirmDeleteVisible = false;
  deleteTarget: UserDataFileDto | null = null;
  deleting = false;

  userDatasets$ = this.buildDatasetsStream();

  private buildDatasetsStream(): Observable<UserDataFileDto[]> {
    return this.userDatasetService.getUserDataList().pipe(
      tap(datasets => datasets.forEach(d => this.initMeta(d))),
      catchError(() => this.datasetsFetchErrorHandling())
    );
  }

  ngOnInit(): void {
    this.settingsService.getAllSettings()
      .pipe(catchError(() => { this.settingsError = true; return EMPTY; }))
      .subscribe(setting => this.maintenanceMode = setting[0].maintenance_mode);

    this.hasNoSpaceLimit = !this.authService.currentUser.space_limit_value;
    this.hasNoSpaceAssigned = this.authService.currentUser.space_limit_value === 1;
    this.dataManagementGroups$ = this.userDatasetService.getDataManagementGroups();

    this.userDatasetService.doRefresh.subscribe(value => {
      if (value) {
        this.userDatasets$ = this.buildDatasetsStream();
      }
    });
  }

  private initMeta(dataset: UserDataFileDto): void {
    if (this.metaMap.has(dataset.id)) return;

    const meta: DatasetMeta = {
      datasetName: signal(''),
      versionName: signal(''),
      variable: {
        shortName: signal(''),
        prettyName: signal(''),
        unit: signal('')
      },
      editDataset: {opened: false},
      editVersion: {opened: false},
      editVariable: {opened: false},
      filePreprocessingStatus: null,
    };
    this.metaMap.set(dataset.id, meta);

    this.datasetService.getDatasetById(dataset.dataset)
      .pipe(catchError(() => this.fetchMetadataError('Dataset')))
      .subscribe(d => meta.datasetName.set(d.pretty_name));

    this.datasetVersionService.getVersionById(dataset.version)
      .pipe(catchError(() => this.fetchMetadataError('Version')))
      .subscribe(v => meta.versionName.set(v.pretty_name));

    this.loadVariable(dataset, meta);
    this.startPreprocessingPolling(dataset, meta);
  }

  getMeta(datasetId: string): DatasetMeta | undefined {
    return this.metaMap.get(datasetId);
  }

  private loadVariable(dataset: UserDataFileDto, meta: DatasetMeta): void {
    this.datasetVariableService.getVariableById(dataset.variable, true)
      .pipe(catchError(() => this.fetchMetadataError('Variable')))
      .subscribe(v => {
        meta.variable.shortName.set(v.short_name);
        meta.variable.prettyName.set(v.pretty_name);
        meta.variable.unit.set(v.unit);
      });
  }

  private startPreprocessingPolling(dataset: UserDataFileDto, meta: DatasetMeta): void {
    if (!dataset.metadata_submitted) {
      meta.filePreprocessingStatus = setInterval(() => {
        this.userDatasetService.getUserDataFileById(dataset.id).subscribe({
          next: (data) => {
            if (data.metadata_submitted) {
              this.loadVariable(data, meta);
              if (meta.variable.prettyName() !== 'none') {
                this.userDatasetService.refresh.next(true);
              }
            }
          },
          error: () => {
            this.userDatasetService.refresh.next(true);
            this.toastService.showErrorWithHeader(
              'File preprocessing failed',
              'File could not be preprocessed. Please make sure you are uploading a proper file.',
              10000
            );
          }
        });
      }, 60 * 1000);
    }
  }

  toggle(datasetId: string, fieldName: string, open: boolean): void {
    const meta = this.metaMap.get(datasetId);
    if (!meta) return;
    if (fieldName === this.datasetFieldName && meta.datasetName()) meta.editDataset.opened = open;
    else if (fieldName === this.versionFieldName && meta.versionName()) meta.editVersion.opened = open;
    else if (fieldName === this.variableFieldName && meta.variable.shortName()) meta.editVariable.opened = open;
  }

  updateMetadata(fieldName: string, fieldValue: string, dataset: UserDataFileDto): void {
    const meta = this.metaMap.get(dataset.id);
    if (!meta) return;
    this.userDatasetService.updateMetadata(fieldName, fieldValue, dataset.id).subscribe({
      next: () => {
        this.toggle(dataset.id, fieldName, false);
        if (fieldName === this.datasetFieldName) meta.datasetName.set(fieldValue);
        if (fieldName === this.versionFieldName) meta.versionName.set(fieldValue);
        if (fieldName === this.variableFieldName) {
          const choice = dataset.all_variables?.find(v => v.name === fieldValue);
          meta.variable.shortName.set(fieldValue);
          meta.variable.prettyName.set(choice?.long_name ?? '');
          meta.variable.unit.set(choice?.units ?? '');
        }
        this.toastService.showSuccess('Metadata has been updated');
      },
      error: () => this.toastService.showError('Metadata could not be updated')
    });
  }

  getTheFileSize(dataset: UserDataFileDto): string {
    return this.userDatasetService.getTheSizeInProperUnits(dataset.file_size);
  }

  getDatasetGroups(dataset: UserDataFileDto, groups: DataManagementGroupsDto[]): DataManagementGroupsDto[] {
    return groups.filter(g => dataset.user_groups.includes(g.id));
  }

  showLogWindow(dataset: UserDataFileDto): void {
    this.logTarget = dataset;
    this.logWindowVisible = true;
  }

  openDeleteDialog(dataset: UserDataFileDto): void {
    this.deleteTarget = dataset;
    this.confirmDeleteVisible = true;
  }

  closeDeleteDialog(): void {
    this.confirmDeleteVisible = false;
    this.deleteTarget = null;
    this.deleting = false;
  }

  confirmDelete(): void {
    if (!this.deleteTarget) return;
    this.deleting = true;
    const obs = this.deleteTarget.is_used_in_validation
      ? this.userDatasetService.deleteUserDataFileOnly(this.deleteTarget.id)
      : this.userDatasetService.deleteUserData(this.deleteTarget.id);

    obs.subscribe({
      next: () => {
        this.metaMap.delete(this.deleteTarget!.id);
        this.userDatasetService.refresh.next(true);
        this.authService.init();
        this.closeDeleteDialog();
      },
      error: (error: CustomHttpError) => {
        this.toastService.showErrorWithHeader(
          error.errorMessage.header,
          'We could not delete your file. Please try again later or contact our support team.'
        );
        this.deleting = false;
      }
    });
  }

  toggleReadMore(): void {
    this.readMore = !this.readMore;
  }

  datasetsFetchErrorHandling(): Observable<never> {
    this.datasetFetchError = true;
    return EMPTY;
  }

  getLimitMessage(): string {
    return this.hasNoSpaceLimit
      ? 'You have no space limit for your data.'
      : `You can use up to ${this.authService.currentUser.space_limit_value / Math.pow(10, 9)} GB space for your data. ` +
        `You still have ${this.userDatasetService.getTheSizeInProperUnits(this.authService.currentUser.space_left)} available.`;
  }

  fetchMetadataError(source: string): Observable<never> {
    this.toastService.showErrorWithHeader(
      'Error fetching metadata',
      `${source} metadata could not be fetched. If the error persists, contact our support team.`
    );
    return EMPTY;
  }
}
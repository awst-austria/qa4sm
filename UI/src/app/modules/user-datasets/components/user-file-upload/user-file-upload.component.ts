import {Component} from '@angular/core';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {BehaviorSubject, Subscription} from 'rxjs';
import {finalize} from 'rxjs/operators';
import {HttpEventType} from '@angular/common/http';
import * as uuid from 'uuid';
import * as JSZip from 'jszip';
import {AuthService} from '../../../core/services/auth/auth.service';
import {UserFileMetadata} from '../../../core/services/form-interfaces/UserFileMetadataForm';
import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {ButtonModule} from 'primeng/button';
import {DialogModule} from 'primeng/dialog';
import {InputTextModule} from 'primeng/inputtext';
import {TooltipModule} from 'primeng/tooltip';

@Component({
  selector: 'qa-user-file-upload',
  templateUrl: './user-file-upload.component.html',
  styleUrls: ['./user-file-upload.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    ButtonModule,
    DialogModule,
    InputTextModule,
    TooltipModule,
  ]
})
export class UserFileUploadComponent {
  file: File;
  fileName = '';
  name = '';
  dialogVisible = false;
  spinnerVisible = false;
  isFileTooBig = false;

  uploadProgress: BehaviorSubject<number> = new BehaviorSubject<number>(0);
  uploadSub: Subscription;
  allowedExtensions = ['.zip', '.nc', '.nc4'];

  uploadObserver = {
    next: (event: any) => this.onUploadNext(event),
    error: (error: any) => this.onUploadError(error),
    complete: () => this.onUploadComplete()
  }

  metadataForm = this.formBuilder.group<UserFileMetadata>({
    dataset_name: [null, [Validators.required, Validators.maxLength(30), Validators.pattern(/^[A-Za-z0-9@+\-_]*$/)]],
    dataset_pretty_name: [null],
    version_name: [null, [Validators.required, Validators.maxLength(30), Validators.pattern(/^[A-Za-z0-9@+\-_]*$/)]],
    version_pretty_name: [null],
  });

  constructor(
    private userDatasetService: UserDatasetsService,
    private formBuilder: FormBuilder,
    private toastService: ToastService,
    public authService: AuthService
  ) {}

  private verifyZipContent(): void {
    const zip = new JSZip.default();
    zip.loadAsync(this.file).then(contents => {
      const files = Object.keys(contents.files).filter(key =>
        !['nc', 'nc4', 'csv', 'yml'].includes(key.split('.').reverse()[0]) && !contents.files[key].dir);
      if (files.length !== 0) {
        this.toastService.showErrorWithHeader('File can not be uploaded',
          'The zip file you are trying to upload contains files with no acceptable extensions (i.e. netCDF or csv + yml');
        this.file = null;
      }
    });
  }

  onFileSelected(event): void {
    this.file = event.target.files[0];
    this.isFileTooBig = false;

    if (this.authService.currentUser.space_left && this.file.size > this.authService.currentUser.space_left) {
      this.isFileTooBig = true;
      this.file = null;
      return null;
    }

    const fileExtension = this.file.name.split('.').reverse()[0];

    if (!this.allowedExtensions.includes('.' + fileExtension)) {
      this.file = null;
      return null;
    }

    if (fileExtension === 'zip') {
      this.verifyZipContent();
    }

    this.fileName = `${uuid.v4()}.${fileExtension}`;
    this.dialogVisible = true;
    event.target.value = null;
  }

  sendForm(): void {
    if (this.file) {
      // copy values to pretty_name
      this.metadataForm.patchValue({
        dataset_pretty_name: this.metadataForm.value.dataset_name,
        version_pretty_name: this.metadataForm.value.version_name,
      });

      this.name = 'uploadedFile';
      this.spinnerVisible = true;
      const upload$ = this.userDatasetService.userFileUpload(this.name, this.file, this.fileName, this.metadataForm.value)
        .pipe(finalize(() => this.reset()));
      this.uploadSub = upload$.subscribe(this.uploadObserver);
    }
  }

  private onUploadNext(event): void {
    if (event.type === HttpEventType.UploadProgress) {
      this.uploadProgress.next(Math.round(100 * (event.loaded / event.total)));
    } else if (event.type === HttpEventType.Response) {
      this.userDatasetService.refresh.next(true);
      this.authService.init();
      this.resetFile();
    }
  }

  private onUploadError(error: any): void {
    let errorMessage = 'File could not be uploaded. Please try again or contact our team.';
    if (error.errorMessage && error.errorMessage.message) {
      errorMessage = error.errorMessage.message;
    }
    this.toastService.showErrorWithHeader('File not saved', errorMessage);
  }

  private onUploadComplete(): void {
    this.metadataForm.reset({});
  }

  onSaveData(): void {
    if (!this.metadataForm.valid) {
      this.dialogVisible = true; // open dialog if names are not filled in
      return;
    }
    this.sendForm();
  }

  closeDialog(): void {
    this.dialogVisible = false;
  }

  resetFile(): void {
    this.file = null;
    this.fileName = null;
  }

  reset(): void {
    this.spinnerVisible = false;
    this.uploadProgress = null;
    this.uploadSub = null;
  }

  getTheFileSize(): string {
    return this.userDatasetService.getTheSizeInProperUnits(this.authService.currentUser.space_left);
  }

  getISMNList(): void {
    this.userDatasetService.getISMNList();
  }

}
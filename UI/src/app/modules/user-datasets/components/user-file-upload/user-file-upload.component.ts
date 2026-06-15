import {Component, HostListener} from '@angular/core';
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
  isDragOver = false;

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


  // ---------- Window guards ----------
  @HostListener('window:dragover', ['$event'])
  onWindowDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  @HostListener('window:drop', ['$event'])
  onWindowDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
  }

  @HostListener('window:dragend')
  onWindowDragEnd(): void {
    this.isDragOver = false;
  }

  // ---------- Drag & drop handlers ----------

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    if (this.authService.currentUser.space_left === 0) {
      return;
    }
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    if (this.authService.currentUser.space_left === 0) {
      return;
    }

    const files = event.dataTransfer?.files;
    if (!files || files.length === 0) {
      return;
    }

    if (files.length > 1) {
      this.toastService.showErrorWithHeader('Too many files',
        'You can upload only one file at a time. Please drop a single .zip, .nc or .nc4 file.');
      return;
    }

    this.handleFile(files[0]);
  }

  // ---------- File handling (shared by input + drop) ----------

  onFileSelected(event): void {
    const file = event.target.files[0];
    event.target.value = null; // reset input
    this.handleFile(file);
  }

  private handleFile(file: File): void {
    if (!file) {
      return;
    }
    this.file = file;
    this.isFileTooBig = false;

    if (this.authService.currentUser.space_left && this.file.size > this.authService.currentUser.space_left) {
      this.isFileTooBig = true;
      this.file = null;
      return;
    }

    const fileExtension = this.file.name.split('.').reverse()[0];

    if (!this.allowedExtensions.includes('.' + fileExtension)) {
      this.toastService.showErrorWithHeader('File can not be uploaded',
        'Accepted file types: .zip, .nc, .nc4');
      this.file = null;
      return;
    }

    if (fileExtension === 'zip') {
      this.verifyZipContent().then(valid => {
        if (valid) {
          this.fileName = `${uuid.v4()}.${fileExtension}`;
          this.dialogVisible = true;
        }
      }).catch(() => {
        this.toastService.showErrorWithHeader('File can not be uploaded',
          'The file is not a valid zip archive or is corrupted.');
        this.file = null;
      });
      return;
    }
    this.fileName = `${uuid.v4()}.${fileExtension}`;
    this.dialogVisible = true;
  }

  private verifyZipContent(): Promise<boolean> {
    const zip = new JSZip.default();
    return zip.loadAsync(this.file).then(contents => {
      const files = Object.keys(contents.files).filter(key =>
        !['nc', 'nc4', 'csv', 'yml'].includes(key.split('.').reverse()[0]) && !contents.files[key].dir);
      if (files.length !== 0) {
        this.toastService.showErrorWithHeader('File can not be uploaded',
          'The zip file you are trying to upload contains files with no acceptable extensions (i.e. netCDF or csv + yml');
        this.file = null;
        return false;
      }
      return true;
    });
  }

  // ---------- Upload ----------

  sendForm(): void {
    if (this.file) {
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
    // The backend leaves a UserDatasetFile record behind on a failed upload,
    // so refresh the list to surface it (as a "Failed" row) and update space usage.
    this.userDatasetService.refresh.next(true);
    this.authService.init();
    this.resetFile();
  }

  private onUploadComplete(): void {
    // Form reset is handled in reset() via finalize, so it also covers the error case.
  }

  // ---------- Dialog actions ----------

  // Single-step "confirm metadata + upload": runs the upload and closes the dialog.
  onSaveData(): void {
    if (!this.metadataForm.valid) {
      return; // Upload button is disabled when invalid; nothing to do.
    }
    this.sendForm();             // starts the upload (spinner dialog appears)
    this.dialogVisible = false;  // close the metadata dialog
  }

  // Dialog dismissed (Cancel / X / mask) WITHOUT starting an upload -> cancel.
  onDialogHide(): void {
    if (!this.spinnerVisible) {
      this.resetFile();
      this.metadataForm.reset({});
    }
  }

  closeDialog(): void {
    this.dialogVisible = false; // triggers onDialogHide() via (onHide)
  }

  resetFile(): void {
    this.file = null;
    this.fileName = null;
  }

  reset(): void {
    this.spinnerVisible = false;
    this.uploadProgress = null;
    this.uploadSub = null;
    this.metadataForm.reset({});   // clear form on BOTH success and error
  }

  getTheFileSize(): string {
    return this.userDatasetService.getTheSizeInProperUnits(this.authService.currentUser.space_left);
  }

  getISMNList(): void {
    this.userDatasetService.getISMNList();
  }

}
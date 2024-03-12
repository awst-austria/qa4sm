import {Component} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {BehaviorSubject, EMPTY, Observable, Subscription} from 'rxjs';
import {catchError, finalize} from 'rxjs/operators';
import {HttpEventType} from '@angular/common/http';
import {allowedNameValidator} from '../../services/allowed-name.directive';
import * as uuid from 'uuid';
import * as JSZip from 'jszip';
import {AuthService} from '../../../core/services/auth/auth.service';
import {UserFileMetadata} from '../../../core/services/form-interfaces/UserFileMetadataForm';
import {CustomHttpError} from '../../../core/services/global/http-error.service';

@Component({
  selector: 'qa-user-file-upload',
  templateUrl: './user-file-upload.component.html',
  styleUrls: ['./user-file-upload.component.scss']
})
export class UserFileUploadComponent {
  // variables to store file information
  file: File;
  fileName = '';
  name = '';
  // variable to open the form
  dialogVisible = false;
  spinnerVisible = false;
  isFileTooBig = false;

  uploadProgress: BehaviorSubject<number> = new BehaviorSubject<number>(0);
  uploadSub: Subscription;
  allowedExtensions = ['.zip', '.nc', '.nc4'];

  uploadObserver = {
    next: event => this.onUploadNext(event),
    complete: () => this.onUploadComplete()
  }

  // dataset file form
  metadataForm = this.formBuilder.group<UserFileMetadata>({
    dataset_name: [null, [Validators.required, Validators.maxLength(30), allowedNameValidator()]],
    dataset_pretty_name: [null, [Validators.maxLength(30), allowedNameValidator(true)]],
    version_name: [null, [Validators.required, Validators.maxLength(30), allowedNameValidator()]],
    version_pretty_name: [null, [Validators.maxLength(30), allowedNameValidator(true)]],
  });

  constructor(private userDatasetService: UserDatasetsService,
              private formBuilder: FormBuilder,
              private toastService: ToastService,
              public authService: AuthService) {
  }

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
    // I need to clean the selected file, otherwise there will be problem with choosing the same file next time
    event.target.value = null;
  }

  sendForm(): void {
    if (this.file) {
      this.name = 'uploadedFile';
      this.spinnerVisible = true;
      const upload$ = this.userDatasetService.userFileUpload(this.name, this.file, this.fileName, this.metadataForm.value)
        .pipe(
          finalize(() => this.reset)
        );

      this.uploadSub = upload$
        .pipe(
          catchError((err: CustomHttpError) => this.onUploadError(err))
        )
        .subscribe(this.uploadObserver);
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

  private onUploadError(error: CustomHttpError): Observable<never> {
    this.spinnerVisible = false;
    this.toastService.showErrorWithHeader('File not saved',
      `File could not be uploaded. Please try again or contact our team.`);
    return EMPTY
  }

  private onUploadComplete(): void {
    this.spinnerVisible = false;
    this.metadataForm.reset({});
  }

  onSaveData(): void {
    this.dialogVisible = false;
  }

  resetFile(): void {
    this.file = null;
    this.fileName = null;
  }

  reset(): void {
    this.uploadProgress = null;
    this.uploadSub = null;
  }

  getTheFileSize(): string {
    return this.userDatasetService.getTheSizeInProperUnits(this.authService.currentUser.space_left);
  }


  getISMNList(): void{
    this.userDatasetService.getISMNList();
  }


}

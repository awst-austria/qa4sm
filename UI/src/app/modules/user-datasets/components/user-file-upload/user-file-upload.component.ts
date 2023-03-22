import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {BehaviorSubject, Subscription} from 'rxjs';
import {finalize} from 'rxjs/operators';
import {HttpEventType} from '@angular/common/http';
import {allowedNameValidator} from '../../services/allowed-name.directive';
import * as uuid from 'uuid';
// @ts-ignore
import JSZip from 'jszip';
import {AuthService} from '../../../core/services/auth/auth.service';

@Component({
  selector: 'qa-user-file-upload',
  templateUrl: './user-file-upload.component.html',
  styleUrls: ['./user-file-upload.component.scss']
})
export class UserFileUploadComponent implements OnInit {
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

  // dataset file form
  metadataForm = this.formBuilder.group({
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

  ngOnInit(): void {
  }

  private verifyZipContent(): void {
    const zip = new JSZip();
    zip.loadAsync(this.file).then(contents => {
      const files = Object.keys(contents.files).filter(key =>
        !['nc', 'nc4', 'csv', 'yml'].includes(key.split('.').reverse()[0]));
      if (files.length !== 0){
        this.toastService.showErrorWithHeader('File can not be uploaded',
          'The zip file you are trying to upload contains files with no acceptable extensions (i.e. netCDF or csv + yml');
        this.file = null;
      }
    });
  }

  onFileSelected(event): void {
    this.file = event.target.files[0];
    this.isFileTooBig = false;

    if (this.authService.currentUser.space_left && this.file.size > this.authService.currentUser.space_left){
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
      const upload$ = this.userDatasetService.userFileUpload(this.name, this.file, this.fileName)
        .pipe(finalize(() => this.reset));

      this.uploadSub = upload$.subscribe(event => {
          if (event.type === HttpEventType.UploadProgress) {
            this.uploadProgress.next(Math.round(100 * (event.loaded / event.total)));
          } else if (event.type === HttpEventType.Response) {
            this.userDatasetService.sendMetadata(this.metadataForm.value, event.body.id).subscribe((response) => {
                if (response.status === 202) {
                  // Request accepted for processing, show a processing message
                  this.toastService.showAlertWithHeader('Metadata processing in progress.',
                    'The metadata is being processed. Please wait for a moment.');
                } else {
                  // Final response received, reset the form and refresh the view
                  this.spinnerVisible = false;
                  this.metadataForm.reset('');
                  this.userDatasetService.refresh.next(true);
                  this.authService.init();
                  this.resetFile();
                }
                // this.userDatasetService.refresh.next(true);
                // this.authService.init();
                // this.resetFile();
                // this.spinnerVisible = false;
                // this.metadataForm.reset('');
              },
              (message) => {
                this.spinnerVisible = false;
                this.toastService.showErrorWithHeader('Metadata not saved.',
                  `${message.error.error}.\n Provided metadata could not be saved. Please try again or contact our team.`);
              },
              () => {
                this.spinnerVisible = false;
                this.metadataForm.reset('');
              });
          }
        },
        (message) => {
          this.spinnerVisible = false;
          this.toastService.showErrorWithHeader('File not saved',
            `${message.error.error}.\n File could not be uploaded. Please try again or contact our team.`);
        }
      );
    }
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


}

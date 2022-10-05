import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {ToastService} from '../../../core/services/toast/toast.service';
import {BehaviorSubject, Subscription} from 'rxjs';
import {finalize} from 'rxjs/operators';
import {HttpEventType} from '@angular/common/http';


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
  queryNameForFile = 'file';

  uploadProgress: BehaviorSubject<number> = new BehaviorSubject<number>(0);
  uploadSub: Subscription;

  // dataset file form
  metadataForm = this.formBuilder.group({
    dataset_name: ['', [Validators.required, Validators.maxLength(30)]],
    dataset_pretty_name: ['', Validators.maxLength(30)],
    version_name: ['', [Validators.required, Validators.maxLength(30)]],
    version_pretty_name: ['', Validators.maxLength(30)],
  });
  formErrors: any;

  variableOptions = [
    {name: 'From file', query_name: this.queryNameForFile},
    {name: 'Provide variable name', query_name: null}
  ];
  unitsOptions = [
    {name: 'From file', query_name: this.queryNameForFile},
    {name: 'Provide variable units', query_name: null}
  ];

  dimensionOptions = [
    {name: 'From file', query_name: this.queryNameForFile},
    {name: 'Provide dimension names', query_name: 'user'}
  ];

  constructor(private userDatasetService: UserDatasetsService,
              private formBuilder: FormBuilder,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
  }

  onFileSelected(event): void {
    this.file = event.target.files[0];
    this.fileName = this.file.name;
    this.dialogVisible = true;
  }

  sendForm(): void {
    if (this.file) {
      this.name = 'uploadedFile';
      this.spinnerVisible = true;
      let upload$ = this.userDatasetService.userFileUpload(this.name, this.file)
        .pipe(finalize(() => this.reset));

      this.uploadSub = upload$.subscribe(event => {
        if (event.type === HttpEventType.UploadProgress) {
          this.uploadProgress.next(Math.round(100 * (event.loaded / event.total)));
        } else if (event.type === HttpEventType.Response) {
          this.userDatasetService.sendMetadata(this.metadataForm.value, event.body.id).subscribe(() => {
              this.userDatasetService.refresh.next(true);
              this.file = null;
              this.fileName = null;
            },
            () => {
              this.spinnerVisible = false;
              this.toastService.showErrorWithHeader('Metadata not saved',
                'Provided metadata could not be saved. Please try again or contact our team.');
            },
            () => {
              this.spinnerVisible = false;
              // this.userDatasetService.refresh.next(true);
            });
        }
      },
        () => {
          this.spinnerVisible = false;
          this.toastService.showErrorWithHeader('File not saved',
            'File could not be uploaded. Please try again or contact our team.');
        }
        );
    }
  }

  onSaveData(): void {
    this.dialogVisible = false;
  }

  reset(): void {
    this.uploadProgress = null;
    this.uploadSub = null;
    // this.userDatasetService.refresh.next(true);
  }

}

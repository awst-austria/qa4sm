import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {ToastService} from '../../../core/services/toast/toast.service';


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
  // fileContent: any;

  // dataset file form
  metadataForm = this.formBuilder.group({
    dataset_name: ['', [Validators.required, Validators.maxLength(30)]],
    dataset_pretty_name: ['', Validators.maxLength(30)],
    version_name: ['', [Validators.required, Validators.maxLength(30)]],
    version_pretty_name: ['', Validators.maxLength(30)],
    variable_name: ['', Validators.required], // dropdown
    variable_units: [''],
    // variable_value_range: [''],
    dimension_name: ['', Validators.required],
  });
  formErrors: any;

  // so far I put some values that will be replaced later
  variableOptions = [
    {name: 'Soil moisture', query_name: 'sm'},
    {name: 'From file', query_name: 'file'}
  ];

  dimensionOptions = [
    {name: 'X-Y-Z', query_name: 'XYZ'},
    {name: 'Lat-Lon-Time', query_name: 'LLT'}
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
      this.userDatasetService.userFileUpload(this.name, this.file).subscribe(data => {
          this.userDatasetService.sendMetadata(this.metadataForm.value, data.id).subscribe(() => {
              this.userDatasetService.refresh.next(true);
            },
            () => {
              this.spinnerVisible = false;
              this.toastService.showErrorWithHeader('Metadata not saved',
                'Provided metadata could not be saved. Please try again or contact our team.');
            });
        },
        () => {
          this.spinnerVisible = false;
          this.toastService.showErrorWithHeader('File not saved',
            'File could not be uploaded. Please try again or contact our team.');
        },
        () => {
          this.spinnerVisible = false;
        });
    }
  }

  onSaveData(): void {
    console.log('Hoorray');
    this.dialogVisible = false;
  }

  // testFile(): void{
  //   const fileReader: FileReader = new FileReader();
  //   // fileReader.onloadend(() => {
  //   //
  //   // } )
  //   const self = this;
  //   // tslint:disable-next-line:only-arrow-functions typedef
  //   fileReader.onloadend = function(x) {
  //     self.fileContent = fileReader.result;
  //   };
  //   fileReader.readAsText(this.file);
  // }


}

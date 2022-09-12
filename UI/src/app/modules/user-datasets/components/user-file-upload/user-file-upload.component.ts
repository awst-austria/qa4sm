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
  queryNameForFile = 'file';
  // fileContent: any;

  // dataset file form
  metadataForm = this.formBuilder.group({
    dataset_name: ['', [Validators.required, Validators.maxLength(30)]],
    dataset_pretty_name: ['', Validators.maxLength(30)],
    version_name: ['', [Validators.required, Validators.maxLength(30)]],
    version_pretty_name: ['', Validators.maxLength(30)],
    // variable_name: ['', Validators.required], // dropdown
    // variable_units: ['', Validators.required],
    // variable_value_range: [''],
    // dimension_name_source: ['', Validators.required],
    // dimension_lon_name: ['', Validators.required],
    // dimension_lat_name: ['', Validators.required],
    // dimension_time_name: ['', Validators.required],
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
    this.metadataForm.controls.variable_name.setValue(this.variableOptions[0].query_name);
    this.metadataForm.controls.variable_units.setValue(this.unitsOptions[0].query_name);
    this.metadataForm.controls.dimension_name_source.setValue(this.dimensionOptions[0].query_name);
    this.setDimensionNames(this.queryNameForFile, this.queryNameForFile, this.queryNameForFile);

    this.metadataForm.get('variable_name').valueChanges.subscribe(() => {
      const varVal = this.metadataForm.controls.variable_name.value;
      if (varVal && varVal !== this.queryNameForFile) {
        this.variableOptions[1].query_name = varVal;
      }
    });

    this.metadataForm.get('variable_units').valueChanges.subscribe(() => {
      const unitsVal = this.metadataForm.controls.variable_units.value;
      if (unitsVal && unitsVal !== this.queryNameForFile) {
        this.unitsOptions[1].query_name = unitsVal;
      }
    });

    this.metadataForm.get('dimension_name_source').valueChanges.subscribe(() => {
      let lonName;
      let latName;
      let timeName;
      const lonVal = this.metadataForm.controls.dimension_lon_name.value;
      const latVal = this.metadataForm.controls.dimension_lat_name.value;
      const timeVal = this.metadataForm.controls.dimension_time_name.value;

      if (lonVal && lonVal !== this.queryNameForFile) {
        lonName = this.metadataForm.controls.dimension_lon_name.value;
      } else {
        lonName = null;
      }

      if (latVal && latVal !== this.queryNameForFile) {
        latName = this.metadataForm.controls.dimension_lat_name.value;
      } else {
        latName = null;
      }

      if (timeVal && timeVal !== this.queryNameForFile) {
        timeName = this.metadataForm.controls.dimension_time_name.value;
      } else {
        timeName = null;
      }
      this.setDimensionNames(lonName, latName, timeName);

    });
  }

  setDimensionNames(lonName, latName, timeName): void {
    this.metadataForm.controls.dimension_lon_name.setValue(lonName);
    this.metadataForm.controls.dimension_lat_name.setValue(latName);
    this.metadataForm.controls.dimension_time_name.setValue(timeName);
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

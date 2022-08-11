import {Component, OnInit} from '@angular/core';
import {FormBuilder, Validators} from '@angular/forms';
import {UserDatasetsService} from '../../services/user-datasets.service';

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

  // dataset file form
  metadataForm = this.formBuilder.group({
    dataset_name: ['', [Validators.required, Validators.maxLength(30)]],
    dataset_pretty_name: ['', Validators.maxLength(30)],
    version_name: ['', [Validators.required, Validators.maxLength(30)]],
    version_pretty_name: ['', Validators.maxLength(30)],
    variable_name: ['', Validators.required], // dropdown
    variable_units: [''],
    variable_value_range: [''],
    dimension_name: ['', Validators.required]
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
              private formBuilder: FormBuilder) {
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
      const upload$ = this.userDatasetService.userFileUpload(this.name, this.file, this.metadataForm.value);
      upload$.subscribe(data => {
        console.log(data);
      });
    }
  }

  onSaveData(): void {
    console.log('Hoorray');
    this.dialogVisible = false;
  }


}

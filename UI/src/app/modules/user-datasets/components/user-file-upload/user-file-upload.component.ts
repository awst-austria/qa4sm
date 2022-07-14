import {Component, OnInit} from '@angular/core';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';

@Component({
  selector: 'qa-user-file-upload',
  templateUrl: './user-file-upload.component.html',
  styleUrls: ['./user-file-upload.component.scss']
})
export class UserFileUploadComponent implements OnInit {
  file: File;
  fileName = '';
  name = '';
  constructor(private validationService: ValidationrunService) { }

  ngOnInit(): void {
  }

  onFileSelected(event): void{
    this.file = event.target.files[0];
    this.fileName = this.file.name;
  }

  sendFile(): void{
    if (this.file) {
      this.name = 'uploadedFile';
      const upload$ = this.validationService.userFileUpload(this.name, this.file, this.fileName);
      upload$.subscribe(data => {
        console.log(data);
      });
    }
  }

}

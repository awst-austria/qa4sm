import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ValidationrunService} from '../core/services/validation-run/validationrun.service';

@Component({
  selector: 'qa-user-file-upload',
  templateUrl: './user-file-upload.component.html',
  styleUrls: ['./user-file-upload.component.scss']
})
export class UserFileUploadComponent implements OnInit {
  fileName = '';
  constructor(private validationService: ValidationrunService) { }

  ngOnInit(): void {
  }

  onFileSelected(event): void{
    const file: File = event.target.files[0];
    if (file) {
      this.fileName = file.name;
      const formData = new FormData();
      formData.append('thumbnail', file);
      const upload$ = this.validationService.userFileUpload(formData);
      upload$.subscribe();
    }
  }

}

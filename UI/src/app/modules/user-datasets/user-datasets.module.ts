import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {UserFileUploadComponent} from './components/user-file-upload/user-file-upload.component';
import {ButtonModule} from 'primeng/button';


@NgModule({
  declarations: [UserFileUploadComponent],
  exports: [
    UserFileUploadComponent
  ],
  imports: [
    CommonModule,
    ButtonModule
  ]
})
export class UserDatasetsModule { }

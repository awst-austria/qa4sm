import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {UserFileUploadComponent} from './components/user-file-upload/user-file-upload.component';
import {ButtonModule} from 'primeng/button';
import {DialogModule} from 'primeng/dialog';
import {RouterModule} from '@angular/router';
import {ReactiveFormsModule} from '@angular/forms';
import {InputTextModule} from 'primeng/inputtext';
import {TooltipModule} from 'primeng/tooltip';
import {DropdownModule} from 'primeng/dropdown';


@NgModule({
  declarations: [UserFileUploadComponent],
  exports: [
    UserFileUploadComponent
  ],
  imports: [
    CommonModule,
    ButtonModule,
    DialogModule,
    RouterModule,
    ReactiveFormsModule,
    InputTextModule,
    TooltipModule,
    DropdownModule
  ]
})
export class UserDatasetsModule { }

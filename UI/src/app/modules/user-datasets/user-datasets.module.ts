import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {UserFileUploadComponent} from './components/user-file-upload/user-file-upload.component';
import {ButtonModule} from 'primeng/button';
import {DialogModule} from 'primeng/dialog';
import {RouterModule} from '@angular/router';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {InputTextModule} from 'primeng/inputtext';
import {TooltipModule} from 'primeng/tooltip';
import {DropdownModule} from 'primeng/dropdown';
import {UserDatasetListComponent} from './components/user-dataset-list/user-dataset-list.component';
import {UserDataRowComponent} from './components/user-data-row/user-data-row.component';
import {PanelModule} from 'primeng/panel';


@NgModule({
  declarations: [UserFileUploadComponent, UserDatasetListComponent, UserDataRowComponent],
  exports: [
    UserFileUploadComponent,
    UserDatasetListComponent,
    UserDataRowComponent
  ],
    imports: [
        CommonModule,
        ButtonModule,
        DialogModule,
        RouterModule,
        ReactiveFormsModule,
        InputTextModule,
        TooltipModule,
        DropdownModule,
        FormsModule,
        PanelModule
    ]
})
export class UserDatasetsModule { }

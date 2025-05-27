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
import {UserDataRowComponent} from './components/user-data-row/user-data-row.component';
import {PanelModule} from 'primeng/panel';
import {AllowedNameDirective} from './services/allowed-name.directive';
import {ScrollPanelModule} from 'primeng/scrollpanel';
import {ShareUserDataComponent} from './components/share-user-data/share-user-data.component';


@NgModule({
  declarations: [UserFileUploadComponent, UserDataRowComponent, ShareUserDataComponent],
    exports: [
        UserFileUploadComponent,
        UserDataRowComponent,
        ShareUserDataComponent
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
    PanelModule,
    ScrollPanelModule,
    AllowedNameDirective
  ]
})
export class UserDatasetsModule { }

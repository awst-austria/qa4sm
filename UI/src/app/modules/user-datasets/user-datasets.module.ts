import {NgModule} from '@angular/core';
import {UserFileUploadComponent} from './components/user-file-upload/user-file-upload.component';
import {RouterModule} from '@angular/router';
import {UserDataRowComponent} from './components/user-data-row/user-data-row.component';
import {AllowedNameDirective} from './services/allowed-name.directive';
import {ShareUserDataComponent} from './components/share-user-data/share-user-data.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [UserFileUploadComponent, UserDataRowComponent, AllowedNameDirective, ShareUserDataComponent],
    exports: [
        UserFileUploadComponent,
        UserDataRowComponent,
        ShareUserDataComponent
    ],
    imports: [
        SharedPrimeNgModule,
        RouterModule,
    ]
})
export class UserDatasetsModule { }

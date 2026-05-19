import {NgModule} from '@angular/core';
import {RouterModule} from '@angular/router';
import {AllowedNameDirective} from './services/allowed-name.directive';
import {ShareUserDataComponent} from './components/share-user-data/share-user-data.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [AllowedNameDirective, ShareUserDataComponent],
    exports: [
        ShareUserDataComponent
    ],
    imports: [
        SharedPrimeNgModule,
        RouterModule,
    ]
})
export class UserDatasetsModule { }

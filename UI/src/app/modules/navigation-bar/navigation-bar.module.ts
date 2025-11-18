import {NgModule} from '@angular/core';
import {NavigationBarComponent} from './components/navigation-bar-header/navigation-bar.component';
import {RouterModule} from '@angular/router';
import {NavigationFooterComponent} from './components/navigation-footer/navigation-footer.component';
import { UserModule } from '../user/user.module';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [NavigationBarComponent, NavigationFooterComponent],
  exports: [
    NavigationBarComponent,
    NavigationFooterComponent
    ],
  imports: [
    SharedPrimeNgModule,
    RouterModule,
    UserModule
    ]
})
export class NavigationBarModule {
}

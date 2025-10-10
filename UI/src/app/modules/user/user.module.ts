import { NgModule } from '@angular/core';
import { LoginComponent } from './login/login.component';
import { UserFormComponent } from './user-form/user-form.component';
import { ConfirmationService } from 'primeng/api';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [
    LoginComponent,
    UserFormComponent
  ],
  exports: [
    LoginComponent,
    UserFormComponent
  ],
  imports: [
   SharedPrimeNgModule
  ],
  providers: [
    ConfirmationService
  ]
})
export class UserModule { }

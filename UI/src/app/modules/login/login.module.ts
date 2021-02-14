import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoginComponent } from './login/login.component';
import {CoreModule} from '../core/core.module';
import {ButtonModule} from 'primeng/button';



@NgModule({
  declarations: [LoginComponent],
  imports: [
    CommonModule,
    CoreModule,
    ButtonModule
  ]
})
export class LoginModule { }

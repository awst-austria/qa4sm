import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { SliderModule } from 'primeng/slider';
import { TooltipModule } from 'primeng/tooltip';
import { LoginComponent } from './login/login.component';
import { UserFormComponent } from './user-form/user-form.component';
import { Select } from 'primeng/select';

@NgModule({
  declarations: [
    UserFormComponent,
    LoginComponent
  ],
  exports: [
    LoginComponent,
    UserFormComponent
  ],
    imports: [
        ButtonModule,
        CheckboxModule,
        CommonModule,
        DialogModule,
        FormsModule,
        InputTextModule,
        PasswordModule,
        ReactiveFormsModule,
        RouterModule,
        SliderModule,
        TooltipModule,
        Select,
    ]
})
export class UserModule { }

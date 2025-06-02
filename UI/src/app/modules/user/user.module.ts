import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { DialogModule } from 'primeng/dialog';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { SliderModule } from 'primeng/slider';
import { TooltipModule } from 'primeng/tooltip';
import { LoginComponent } from './login/login.component';
import { UserFormComponent } from './user-form/user-form.component';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ConfirmationService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { DividerModule } from 'primeng/divider';

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
    ButtonModule,
    CheckboxModule,
    CommonModule,
    ConfirmDialogModule,
    DialogModule,
    DropdownModule,
    FormsModule,
    InputTextModule,
    PasswordModule,
    ReactiveFormsModule,
    RouterModule,
    SliderModule,
    TooltipModule,
    ToastModule,
    DividerModule
  ],
  providers: [
    ConfirmationService
  ]
})
export class UserModule { }

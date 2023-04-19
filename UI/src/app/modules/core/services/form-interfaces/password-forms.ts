import {AbstractControl} from '@angular/forms';


export interface PasswordForm {
  password1: AbstractControl<string>;
  password2: AbstractControl<string>;
}
export interface PasswordResetForm{
  email: AbstractControl<string>;
}

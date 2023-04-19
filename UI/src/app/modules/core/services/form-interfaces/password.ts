import {AbstractControl} from '@angular/forms';


export interface PasswordValidatorForm{
  password1: AbstractControl<string>;
  password2: AbstractControl<string>;
}
export interface PasswordResetForm{
  email: AbstractControl<string>;
}

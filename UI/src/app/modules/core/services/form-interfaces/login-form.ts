import {AbstractControl} from '@angular/forms';

export interface LoginForm{
  identifier: AbstractControl<string>;
  password: AbstractControl<string>;
}

import {AbstractControl} from '@angular/forms';

export interface LoginForm{
  username: AbstractControl<string>;
  password: AbstractControl<string>;
}

import {FormControl, FormGroup} from '@angular/forms';
import {PasswordForm} from '../core/services/form-interfaces/password-forms';

export class PasswordValidator {
  static validPasswordConfirmation(fg: FormGroup<PasswordForm>): any {
    const pass1: FormControl<string> = fg.controls.password1 as FormControl<string>;
    const pass2: FormControl<string> = fg.controls.password2 as FormControl<string>;

    if (pass1.value === pass2.value) {
      return null;
    } else {
      return {validPasswordConfirmation: true};
    }
  }


}

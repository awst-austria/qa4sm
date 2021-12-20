import {FormControl, FormGroup} from '@angular/forms';

export class PasswordValidator {
  static validPasswordConfirmation(fg: FormGroup): any {
    const pass1: FormControl = fg.controls.password1 as FormControl;
    const pass2: FormControl = fg.controls.password2 as FormControl;

    if (pass1.value === pass2.value) {
      return null;
    } else {
      return {validPasswordConfirmation: true};
    }
  }
}

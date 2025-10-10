import {Directive} from '@angular/core';
import {AbstractControl, NG_VALIDATORS, ValidationErrors, Validator, ValidatorFn} from '@angular/forms';

export function allowedNameValidator(spaceAllowed= false): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const chars = spaceAllowed ? /[a-z|A-Z0-9@.+_\- ]/i : /[a-z|A-Z0-9@.+_\-]/i;
    const allowed = [];
    if (control.value){
      control.value.split('').forEach(char => {
        allowed.push(chars.test(char));
      });
    }
    return allowed.every(val => val) ? null : {forbiddenName: {value: control.value}};
  };
}

@Directive({
    selector: '[qaAllowedName]',
    providers: [{ provide: NG_VALIDATORS, useExisting: AllowedNameDirective, multi: true }],
    standalone: false
})
export class AllowedNameDirective implements Validator {

  validate(control: AbstractControl): ValidationErrors | null {
    return  allowedNameValidator()(control);
  }
}

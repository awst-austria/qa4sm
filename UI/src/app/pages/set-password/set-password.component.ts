import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {PasswordValidator} from '../../modules/user/password.validator';
import {PasswordForm} from '../../modules/core/services/form-interfaces/password-forms';
import {EMPTY, Observable} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {CustomHttpError} from '../../modules/core/services/global/http-error.service';

@Component({
  selector: 'qa-set-password',
  templateUrl: './set-password.component.html',
  styleUrls: ['./set-password.component.scss']
})
export class SetPasswordComponent implements OnInit {
  token: string;
  setPasswordForm = new FormGroup<PasswordForm>({
    password1: new FormControl('', [Validators.required]),
    password2: new FormControl('', [Validators.required]),
  }, (formGroup: FormGroup<PasswordForm>) => {
    return PasswordValidator.validPasswordConfirmation(formGroup);
  });
  formErrors: any;
  userAuthenticated: boolean;

  constructor(private authService: AuthService,
              private router: Router,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.authService.isAuthenticated().subscribe(isAuthenticated => {
      this.userAuthenticated = isAuthenticated;
      if (isAuthenticated) {
        this.setPasswordForm.addControl(
          'oldPassword',
          new FormControl('', [Validators.required]),
        )
      }
    })

    this.setPasswordForm.valueChanges.subscribe(() => {
      this.formErrors = null; // Clear form-level errors
    });


    this.authService.passwordResetToken$.subscribe(tkn => {
      this.token = tkn;
    });
  }

  onSubmit(): void {
    let passUpdate: Observable<any>;
    if (this.userAuthenticated) {
      passUpdate = this.updatePassword();
    } else {
      passUpdate = this.resetPassword();
    }
    passUpdate
      .pipe(
        catchError(error => this.onSetPasswordError(error))
      )
      .subscribe(
        () => this.onSetPasswordNext()
      );
  }

  private resetPassword() {
    const setPasswordFormToSubmit = {
      token: this.token,
      password: this.setPasswordForm.controls.password1.value
    };
    return this.authService.resetPassword(setPasswordFormToSubmit, this.token);
  }

  private updatePassword() {
    const updatePasswordForm = {
      old_password: this.setPasswordForm.controls.oldPassword.value,
      new_password: this.setPasswordForm.controls.password1.value,
      confirm_password: this.setPasswordForm.controls.password2.value,
    }
    return this.authService.updatePassword(updatePasswordForm);
  }

  private onSetPasswordNext(): void {
    this.router.navigate(['home'], {queryParams: {showLogin: 'true'}}).then(() =>
      this.toastService.showSuccessWithHeader('Password changed', 'You can log in using the new password'));
  }


  private onSetPasswordError(error: CustomHttpError): Observable<never> {
    this.formErrors = error.errorMessage.message;
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
    return EMPTY
  }

  goBackToProfile(){
    this.router.navigate(['/user-profile']);
  }

}

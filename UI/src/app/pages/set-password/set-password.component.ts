import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {Router} from '@angular/router';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {PasswordValidator} from '../../modules/user/password.validator';
import {PasswordForm} from '../../modules/core/services/form-interfaces/password-forms';
import {EMPTY, Observable, Subscription} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {CustomHttpError} from '../../modules/core/services/global/http-error.service';

@Component({
  selector: 'qa-set-password',
  templateUrl: './set-password.component.html',
  styleUrls: ['./set-password.component.scss']
})
export class SetPasswordComponent implements OnInit, OnDestroy {
  token: string;
  setPasswordForm = new FormGroup<PasswordForm>({
    password1: new FormControl<string>('', [Validators.required]),
    password2: new FormControl<string>('', [Validators.required]),
  }, (formGroup: FormGroup<PasswordForm>) => {
    return PasswordValidator.validPasswordConfirmation(formGroup);
  });
  formErrors: any;

  sub = new Subscription;

  constructor(private authService: AuthService,
              private router: Router,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.authService.passwordResetToken$.subscribe(tkn => {
      this.token = tkn;
    });
  }

  onSubmit(): void {
    const setPasswordFormToSubmit = {
      token: this.token,
      password: this.setPasswordForm.controls.password1.value
    };
    this.sub = this.authService.setPassword(setPasswordFormToSubmit, this.token)
      .pipe(
        catchError(error => this.onSetPasswordError(error))
      )
      .subscribe(
        () => this.onSetPasswordNext()
      );
  }

  private onSetPasswordNext(): void {
    this.router.navigate(['/login']).then(() =>
      this.toastService.showSuccessWithHeader('Password changed', 'You can log in using the new password'));
  }

  private onSetPasswordError(error: CustomHttpError): Observable<never> {
    this.formErrors = error.errorMessage.message;
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
    return EMPTY
  }

  ngOnDestroy() {
    console.log(this.sub);
  }
}

import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {ActivatedRoute, Router} from '@angular/router';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {PasswordValidator} from '../../modules/user/password.validator';
import {PasswordForm} from '../../modules/core/services/form-interfaces/password-forms';

@Component({
  selector: 'qa-set-password',
  templateUrl: './set-password.component.html',
  styleUrls: ['./set-password.component.scss']
})
export class SetPasswordComponent implements OnInit {
  token: string;
  setPasswordForm = new FormGroup<PasswordForm>({
    password1: new FormControl<string>('', [Validators.required]),
    password2: new FormControl<string>('', [Validators.required]),
  }, (formGroup: FormGroup<PasswordForm>) => {
    return PasswordValidator.validPasswordConfirmation(formGroup);
  });
  formErrors: any;

  setPasswordObserver = {
    next: () => this.onSetPasswordNext(),
    error: errors => this.onSetPasswordError(errors)
  }

  constructor(private authService: AuthService,
              private route: ActivatedRoute,
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
    this.authService.setPassword(setPasswordFormToSubmit, this.token).subscribe(
      this.setPasswordObserver
    );
  }

  private onSetPasswordNext(): void{
    this.router.navigate(['/login']).then(() =>
      this.toastService.showSuccessWithHeader('Password changed', 'You can log in using the new password'));
  }

  private onSetPasswordError(errors): void{
    this.formErrors = errors.error;
  }
}

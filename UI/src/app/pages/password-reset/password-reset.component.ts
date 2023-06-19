import {Component} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {Router} from '@angular/router';
import {PasswordResetForm} from '../../modules/core/services/form-interfaces/password-forms';

@Component({
  selector: 'qa-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.scss']
})
export class PasswordResetComponent {


  resetPasswordForm = new FormGroup<PasswordResetForm>({
    email: new FormControl<string>('', [Validators.required, Validators.email]),
  });
  formErrors: any;

  resetPasswordObserver = {
    next: response => this.onResetPasswordNext(response),
    error: error => this.onResetPasswordError(error)
  }

  constructor(private authService: AuthService,
              private router: Router) {
  }

  onSubmit(): void {
    this.authService.resetPassword(this.resetPasswordForm.value).subscribe(
      this.resetPasswordObserver
    );
  }

  private onResetPasswordNext(response): void {
    if (response.status === 'OK') {
      this.router.navigate(['password-reset-done']);
    }
  }

  private onResetPasswordError(error): void {
    this.formErrors = error.error;
  }
}

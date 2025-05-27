import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../modules/core/services/auth/auth.service';
import { Router } from '@angular/router';
import { PasswordResetForm } from '../../modules/core/services/form-interfaces/password-forms';
import { ToastService } from '../../modules/core/services/toast/toast.service';
import { catchError } from 'rxjs/operators';
import { EMPTY, Observable } from 'rxjs';
import { CustomHttpError } from '../../modules/core/services/global/http-error.service';

@Component({
  selector: 'qa-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.scss'],
  standalone: false
})
export class PasswordResetComponent {


  resetPasswordForm = new FormGroup<PasswordResetForm>({
    email: new FormControl<string>('', [Validators.required, Validators.email]),
  });
  errorMessage: string | undefined = undefined;

  resetPasswordObserver = {
    next: (response: { status: string; }) => this.onResetPasswordNext(response),
  }

  constructor(private authService: AuthService,
              private router: Router,
              private toastService: ToastService) {
  }

  onSubmit(): void {
    this.authService.resetPasswordRequest(this.resetPasswordForm.value)
      .pipe(
        catchError(err => this.onResetPasswordError(err))
      )
      .subscribe(
        this.resetPasswordObserver
      );
  }

  private onResetPasswordNext(response: { status: string; }): void {
    if (response.status === 'OK') {
      this.router.navigate(['password-reset-done'])
        .then(() => this.toastService
          .showSuccessWithHeader('Request sent.', 'Check your email for further instructions.'));
    }
  }

  private onResetPasswordError(error: CustomHttpError): Observable<never> {
    this.errorMessage = error.errorMessage.header;
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message);
    return EMPTY
  }
}

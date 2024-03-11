import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {ActivatedRoute, Router} from '@angular/router';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {EMPTY, Observable} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {CustomHttpError} from '../../modules/core/services/global/http-error.service';

@Component({
  selector: 'qa-password-reset-validate-token',
  templateUrl: './password-reset-validate-token.component.html',
  styleUrls: ['./password-reset-validate-token.component.scss']
})
export class PasswordResetValidateTokenComponent implements OnInit {
  tokenError = 0;

  constructor(private authService: AuthService,
              private route: ActivatedRoute,
              private router: Router,
              private toastService: ToastService) {
  }


  ngOnInit(): void {
    this.validateToken();
  }

  validateToken(): void {
    this.route.params.subscribe(params => {
      // check if the passed token is valid, if there is no error use onValidateTokenNext method
      this.authService.validateResetPasswordToken(params.token)
        .pipe(
          catchError(error => this.onValidateTokenError(error))
        )
        .subscribe(response => this.onValidateTokenNext(response, params.token));
    });
  }

  private onValidateTokenNext(response: { status: string; }, token: string): void {
      // set token and navigate to set password page
      this.authService.setPasswordResetToken(token);
      this.router.navigate(['set-password']);
  }

  private onValidateTokenError(error: CustomHttpError): Observable<never> {
    // it is an external package that handles password reset, therefore I have no impact on the error message;
    // when the token doesn't exist anymore, the error will have status 404, any other case suggests other server issue
    let header = error.status === 404 ? 'Invalid password reset link' : 'Something went wrong.'
    let message = error.status === 404
      ? "Possibly the link has been already used. Please request a new password reset."
      :'Setting new password is currently not possible. Please try again later or contact our support team.'
    this.toastService.showErrorWithHeader(header, message)
    this.tokenError = error.status;
    return EMPTY
  }

}

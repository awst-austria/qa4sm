import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../modules/core/services/auth/auth.service';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastService } from '../../modules/core/services/toast/toast.service';
import { EMPTY, Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { CustomHttpError } from '../../modules/core/services/global/http-error.service';

@Component({
  selector: 'qa-password-reset-validate-token',
  templateUrl: './password-reset-validate-token.component.html',
  styleUrls: ['./password-reset-validate-token.component.scss'],
  standalone: false
})
export class PasswordResetValidateTokenComponent implements OnInit {
  tokenError = undefined;

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
    this.toastService.showErrorWithHeader(error.errorMessage.header, error.errorMessage.message)
    this.tokenError = error.errorMessage.header.toLowerCase().includes('something');
    return EMPTY
  }

}

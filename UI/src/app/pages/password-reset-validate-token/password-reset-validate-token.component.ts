import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'qa-password-reset-validate-token',
  templateUrl: './password-reset-validate-token.component.html',
  styleUrls: ['./password-reset-validate-token.component.scss']
})
export class PasswordResetValidateTokenComponent implements OnInit {
  tokenValid = true;
  constructor(private authService: AuthService,
              private route: ActivatedRoute,
              private router: Router) { }


  ngOnInit(): void {
    if (this.router.url !== '/password-reset/set-password'){
      this.validateToken();
    }
  }

  validateToken(): void{
    this.route.params.subscribe(params => {

      const validateTokenObserver = {
        next: response => this.onValidateTokenNext(response, params),
        error: () => this.onValidateTokenError(),
        complete: () => this.onValidateTokenComplete()
      }

      this.authService.validateResetPasswordToken(params.token).subscribe(validateTokenObserver);
    });
  }

  private onValidateTokenNext(response, params): void{
    if (response.status === 'OK'){
      this.authService.setPasswordResetToken(params.token);
    } else {
      this.tokenValid = false;
    }
  }

  private onValidateTokenError(): void{
    this.tokenValid = false;
  }

  private onValidateTokenComplete(): void{
    this.router.navigate(['set-password']);
  }
}

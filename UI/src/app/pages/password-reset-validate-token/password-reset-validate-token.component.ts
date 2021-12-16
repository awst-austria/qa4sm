import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'qa-password-reset-validate-token',
  templateUrl: './password-reset-validate-token.component.html',
  styleUrls: ['./password-reset-validate-token.component.scss']
})
export class PasswordResetValidateTokenComponent implements OnInit {
  // token: string;
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
      this.authService.validateResetPasswordToken(params.token).subscribe(response => {
        if (response.status === 'OK'){
          this.authService.setResetPasswordToken(params.token);
        }
      },
        () => {},
        () => {
          this.router.navigate(['set-password']);
        });
    });

  }
}

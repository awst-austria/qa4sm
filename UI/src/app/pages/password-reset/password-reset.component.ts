import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {Router} from '@angular/router';
import {PasswordResetForm} from '../../modules/core/services/form-interfaces/password-forms';

@Component({
  selector: 'qa-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.scss']
})
export class PasswordResetComponent implements OnInit {


  resetPasswordForm = new FormGroup<PasswordResetForm>({
    email: new FormControl<string>('', [Validators.required, Validators.email]),
  });
  formErrors: any;
  constructor(private authService: AuthService,
              private router: Router) { }

  ngOnInit(): void {
  }

  onSubmit(): void{
    this.authService.resetPassword(this.resetPasswordForm.value).subscribe(response => {
      if (response.status === 'OK'){
        this.router.navigate(['password-reset-done']);
      }
    },
      (errors) => {
        this.formErrors = errors.error;
      });
  }
}

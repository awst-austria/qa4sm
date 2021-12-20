import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {ActivatedRoute, Router} from '@angular/router';
import {ToastService} from '../../modules/core/services/toast/toast.service';
import {PasswordValidator} from '../../modules/user/password.validator';

@Component({
  selector: 'qa-set-password',
  templateUrl: './set-password.component.html',
  styleUrls: ['./set-password.component.scss']
})
export class SetPasswordComponent implements OnInit {
  token: string;
  setPasswordForm = new FormGroup({
    password1: new FormControl('', [Validators.required]),
    password2: new FormControl('', [Validators.required]),
  }, (formGroup: FormGroup) => {
    return PasswordValidator.validPasswordConfirmation(formGroup);
  });
  formErrors: any;

  constructor(private authService: AuthService,
              private route: ActivatedRoute,
              private router: Router,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.authService.checkPasswordResetToken().subscribe(tkn => {
      this.token = tkn;
    });
  }

  onSubmit(): void {
    const setPasswordFormToSubmit = {
      token: this.token,
      password: this.setPasswordForm.controls.password1.value
    };
    this.authService.setPassword(setPasswordFormToSubmit, this.token).subscribe(() => {
        this.router.navigate(['/login']).then(() =>
          this.toastService.showSuccessWithHeader('Password changed', 'You can log in using the new password'));
      },
      (errors) => {
        this.formErrors = errors.error;
      },
    );
  }
}

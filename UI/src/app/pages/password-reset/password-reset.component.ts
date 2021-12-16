import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {Router} from '@angular/router';

@Component({
  selector: 'qa-password-reset',
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.scss']
})
export class PasswordResetComponent implements OnInit {


  resetPasswordForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
  });
  constructor(private authService: AuthService,
              private router: Router) { }

  ngOnInit(): void {
  }

  onSubmit(): void{
    console.log('reset my password', this.resetPasswordForm.value);
    this.authService.resetPassword(this.resetPasswordForm.value).subscribe(response => {
      console.log(response);
      if (response.status === 'OK'){
        this.router.navigate(['password-reset-done']);
      }
    });
  }
}

import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {ActivatedRoute} from '@angular/router';

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
  });
  formErrors: any;

  constructor(private authService: AuthService,
              private route: ActivatedRoute) { }

  ngOnInit(): void {
    // this.route.params.subscribe(params => {
    //   this.token = params.token;
    // });
  }

  onSubmit(): void{

    // console.log(this.token);
    // console.log('reset my password', setPasswordFormToSubmit);

    this.route.params.subscribe(params => {
      const tkn = params.token;
      const setPasswordFormToSubmit = {
        token: tkn,
        password: this.setPasswordForm.controls.password1.value
      };
      this.authService.setPassword(setPasswordFormToSubmit, tkn).subscribe(response => {
      },
        (errors) => {
        // console.log(errors.error.password);
        this.formErrors = errors.error;
        },
        );
    });
  }
}

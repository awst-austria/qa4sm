import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {LoginDto} from '../../modules/core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  providers: []
})
export class LoginComponent implements OnInit {

  loginDto = new LoginDto('', '');
  submitted = false;

  loginForm = new FormGroup({
    username: new FormControl(this.loginDto.username, Validators.required),
    password: new FormControl(this.loginDto.password, Validators.required),
  });

  formMessages = [];

  constructor(private loginService: AuthService, private router: Router) {
  }

  ngOnInit(): void {
  }

  onSubmit() {
    this.submitted = true;
    console.log(this.loginDto);
    this.loginDto.username = this.loginForm.value.username;
    this.loginDto.password = this.loginForm.value.password;


    this.loginService.login(this.loginDto).subscribe(authenticated => {
      if (authenticated) {
        this.router.navigate(['user-profile']);
      } else {

      }
    });
  }

  get diagnostic() {
    return JSON.stringify(this.loginDto);
  }

  loginClick() {
    console.info('clicked');

  }
}

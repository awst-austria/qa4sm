import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../core/services/auth/auth.service';
import {LoginDto} from '../../core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {ToastService} from '../../core/services/toast/toast.service';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  providers: []
})
export class LoginComponent implements OnInit {

  loginDto = new LoginDto('', '');
  submitted = false;
  prevUrl = '';

  loginForm = new FormGroup({
    username: new FormControl(this.loginDto.username, Validators.required),
    password: new FormControl(this.loginDto.password, Validators.required),
  });

  formMessages = [];

  constructor(private loginService: AuthService, private router: Router, private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.loginService.checkPreviousUrl().subscribe(previousUrl => {
      this.prevUrl = previousUrl;
    });
  }

  onSubmit() {

    this.submitted = true;
    this.loginDto.username = this.loginForm.value.username;
    this.loginDto.password = this.loginForm.value.password;


    this.loginService.login(this.loginDto).subscribe(authenticated => {
      if (authenticated) {
        this.router.navigate([this.prevUrl]).then(
          value => this.toastService.showSuccessWithHeader('Successful login', 'Welcome ' + this.loginService.currentUser.username));
      } else {
        this.toastService.showErrorWithHeader('Login failed', 'Wrong username or password');
      }
    });
  }

  get diagnostic() {
    return JSON.stringify(this.loginDto);
  }
}

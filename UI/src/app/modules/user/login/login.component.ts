import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {AuthService} from '../../core/services/auth/auth.service';
import {LoginDto} from '../../core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {ToastService} from '../../core/services/toast/toast.service';
import {LoginForm} from '../../core/services/form-interfaces/login-form';
import {HttpErrorResponse} from '@angular/common/http';


@Component({
  selector: 'qa-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'], 
  providers: []
})
export class LoginComponent {
  @Input() navigateAfter: boolean;
  @Output() loggedIn = new EventEmitter();

  loginDto = new LoginDto('', '');

  loginForm = new FormGroup<LoginForm>({
    username: new FormControl<string>(this.loginDto.username, Validators.required),
    password: new FormControl<string>(this.loginDto.password, Validators.required),
  });

  constructor(private loginService: AuthService,
              private toastService: ToastService) {
  }

  onSubmit() {
    if (this.loginForm.valid) {
      const credentials = new LoginDto(
        this.loginForm.get('username')?.value,
        this.loginForm.get('password')?.value
      );  
    
    this.loginService.login(credentials).subscribe({
      next: (user) => {
        this.loggedIn.emit(true);
        this.toastService.showSuccessWithHeader(
          'Login successful', 
          `Welcome ${user.first_name || user.username}`
        );
      },
      error: (error) => {
        this.handleLoginError(error);
      }
    });
    }
  }

  private handleLoginError(error: HttpErrorResponse) {
    if (error.status === 401) {
      this.toastService.showErrorWithHeader('Login failed', 'Username or password incorrect.');
    } else {
      this.toastService.showErrorWithHeader('Login failed', 'An error occurred while trying to log in, please try again later.');
    }
  }

  onForgotOrSignUpClick(){
    this.loginService.showLoginModalSubject.next(false);
  }
}

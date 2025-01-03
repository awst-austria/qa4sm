import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {AuthService} from '../../core/services/auth/auth.service';
import {LoginDto} from '../../core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {ToastService} from '../../core/services/toast/toast.service';
import {LoginForm} from '../../core/services/form-interfaces/login-form';
import {HttpErrorResponse} from '@angular/common/http';
import {Subject, takeUntil} from 'rxjs';


@Component({
  selector: 'qa-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'], 
  providers: []
})
export class LoginComponent implements OnInit {
  @Input() navigateAfter: boolean;
  @Output() loggedIn = new EventEmitter();

  showModal = false;
  isLoading = false;
  private destroy$ = new Subject<void>();
  headerMessage = 'Please log in';

  loginDto = new LoginDto('', '');

  loginForm = new FormGroup<LoginForm>({
    username: new FormControl<string>(this.loginDto.username, Validators.required),
    password: new FormControl<string>(this.loginDto.password, Validators.required),
  });

  constructor(private loginService: AuthService,
              private toastService: ToastService) {
  }

  ngOnInit() {
    this.loginService.showLoginModal$
      .pipe(takeUntil(this.destroy$))
      .subscribe(state => {
        this.showModal = state.show;
        if (state.message) {
          this.headerMessage = state.message;
        } else {
          this.headerMessage = 'Please log in';
        }
        if (!state.show) {
          this.resetForm();
        }
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
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

  private resetForm() {
    this.loginForm.reset();
    this.isLoading = false;
  }

  onWindowHide() {
    this.loginService.hideLoginModal();
  }

  private handleLoginError(error: HttpErrorResponse) {
    if (error.status === 401) {
      this.toastService.showErrorWithHeader('Login failed', 'Username or password incorrect.');
    } else {
      this.toastService.showErrorWithHeader('Login failed', 'An error occurred while trying to log in, please try again later.');
    }
  }

  onForgotOrSignUpClick(){
    this.loginService.hideLoginModal();
  }
}

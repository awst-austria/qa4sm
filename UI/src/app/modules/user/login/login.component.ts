import {Component, EventEmitter, Input, OnInit, Output, signal, ViewChild} from '@angular/core';
import {AuthService} from '../../core/services/auth/auth.service';
import {LoginDto} from '../../core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {ToastService} from '../../core/services/toast/toast.service';
import {LoginForm} from '../../core/services/form-interfaces/login-form';
import {HttpErrorResponse} from '@angular/common/http';
import {Subject, takeUntil} from 'rxjs';
import {Router, NavigationEnd} from '@angular/router';


@Component({
  selector: 'qa-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'], 
  providers: []
})
export class LoginComponent implements OnInit {

  @Output() loggedIn = new EventEmitter();
  isHomePage = signal<boolean | undefined>(undefined)

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
              private toastService: ToastService,
              private router: Router) {}

  ngOnInit() {
    
    //set isHomePage boolean value based on the current route
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.isHomePage.set(event.url.includes('/home'))
      }
    });

    // open login modal on showLoginModal$ observable
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


  get isHomePageValue(): boolean {
    // is homepage boolean getter 
    return this.isHomePage();
  }

  get dialogClasses(): string {
    // get p dialog classes for login modal colour scheme 
    const baseClass = 'login-dialog';
    return this.isHomePageValue ? `${baseClass} home-page-modal` : baseClass;
  }

  ngOnDestroy() {
    // unsubscribe from the destroy$ subject
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

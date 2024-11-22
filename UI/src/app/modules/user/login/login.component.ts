import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {AuthService} from '../../core/services/auth/auth.service';
import {LoginDto} from '../../core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {ToastService} from '../../core/services/toast/toast.service';
import {LoginForm} from '../../core/services/form-interfaces/login-form';


@Component({
  selector: 'qa-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  providers: []
})
export class LoginComponent implements OnInit {
  @Input() navigateAfter: boolean;
  @Output() loggedIn = new EventEmitter();

  loginDto = new LoginDto('', '');
  submitted = false;
  prevUrl = '';

  loginForm = new FormGroup<LoginForm>({
    identifier: new FormControl<string>(this.loginDto.identifier, Validators.required),
    password: new FormControl<string>(this.loginDto.password, Validators.required),
  });

  constructor(private loginService: AuthService,
              private router: Router,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    this.loginService.previousUrl$.subscribe(previousUrl => this.prevUrl = previousUrl);
  }

  onSubmit() {

    this.submitted = true;
    this.loginDto.identifier = this.loginForm.value.identifier;
    this.loginDto.password = this.loginForm.value.password;


    this.loginService.login(this.loginDto).subscribe({
      next: data => {
        if (this.navigateAfter) {
          this.router.navigate([this.prevUrl]).then(() => {
            this.toastService.showSuccessWithHeader('Successful login', 'Welcome ' + (this.loginService.currentUser.first_name ? this.loginService.currentUser.first_name : this.loginService.currentUser.username));
          });
        } else {
          this.loggedIn.emit(true);
          this.toastService.showSuccessWithHeader('Successful login', 'Welcome ' + (this.loginService.currentUser.first_name ? this.loginService.currentUser.first_name : this.loginService.currentUser.username));
        }
      },
      error: (error) => {
        if (error.status === 401) {
          this.toastService.showErrorWithHeader('Login failed', 'Wrong username/email or password');
        } else {
          this.toastService.showErrorWithHeader('Login failed', 'An error occurred during login, please try again later');
        }
      }
    });

  }
}

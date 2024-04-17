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
    username: new FormControl<string>(this.loginDto.username, Validators.required),
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
    this.loginDto.username = this.loginForm.value.username;
    this.loginDto.password = this.loginForm.value.password;


    // todo: this one should be rewritten the way, that it handles login entirely and sets the current user,
    // also the message should be updated; it's not only wrong credentials that may fail
    this.loginService.login(this.loginDto).subscribe(authenticated => {
      if (authenticated && this.navigateAfter) {
        this.router.navigate([this.prevUrl]).then(
          value => this.toastService.showSuccessWithHeader('Successful login', 'Welcome ' + this.loginService.currentUser.username));
      } else if (authenticated && !this.navigateAfter) {
        this.loggedIn.emit(authenticated);
        this.toastService.showSuccessWithHeader('Successful login', 'Welcome ' + this.loginService.currentUser.username);
      } else {
        this.toastService.showErrorWithHeader('Login failed', 'Wrong username or password');
      }
    });
  }
}

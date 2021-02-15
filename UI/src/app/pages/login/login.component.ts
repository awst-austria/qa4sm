import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {LoginDto} from '../../modules/core/services/auth/login.dto';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MessageService} from 'primeng/api';
import {Router} from '@angular/router';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  providers: [MessageService]
})
export class LoginComponent implements OnInit {

  loginDto = new LoginDto('', '');
  submitted = false;

  loginForm = new FormGroup({
    username: new FormControl(this.loginDto.username, Validators.required),
    password: new FormControl(this.loginDto.password, Validators.required),
  });

  formMessages = [];

  constructor(private loginService: AuthService, private messageService: MessageService, private router: Router) {
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
        this.messageService.add({
          severity: 'success',
          summary: 'You are logged in',
          detail: 'Welcome ' + this.loginService.currentUser.username
        });
        this.router.navigate(['user-profile']);
      } else {
        this.messageService.add({severity: 'error', summary: 'Authentication error', detail: 'Wrong username or password'});
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

import { Component, OnInit } from '@angular/core';
import {LoginService} from '../../modules/login/login.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  constructor(private loginService: LoginService) { }

  ngOnInit(): void {
  }

  loginClick() {
    console.info('clicked')
    this.loginService.login();
  }
}

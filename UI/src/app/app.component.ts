import {Component, OnInit, ViewChild} from '@angular/core';
import {NGXLogger} from 'ngx-logger';
import { AuthService } from './modules/core/services/auth/auth.service';
import { LoginComponent } from './modules/user/login/login.component';



@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'qa4sm-ui';
  showLoginModal = false;
  @ViewChild(LoginComponent) loginComponent: LoginComponent;


  constructor(private logger: NGXLogger, private authService: AuthService) {
    this.authService.showLoginModal$.subscribe(
      show => this.showLoginModal = show
    );
  }

  ngOnInit(): void {
    this.logger.debug('Main app component init');
  }

  onLoginSuccess() {
    this.authService.hideLoginModal();
  }

  onLoginModalClose() {
    if (this.loginComponent) {
      this.loginComponent.loginForm.reset();
    }
  }
}

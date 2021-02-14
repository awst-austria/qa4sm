import {Injectable} from '@angular/core';
import {AuthService} from '../core/services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class LoginService {

  constructor(private authService: AuthService) {
  }

  login() {
    console.info('Bump')
    this.authService.test();
  }
}

import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, from} from 'rxjs';
import {LoginDto} from './login.dto';
import {NGXLogger} from 'ngx-logger';
import {UserDto} from './user.dto';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = environment.API_URL;

  private authUrl = this.API_URL + 'api/auth';
  private testUrl = this.API_URL + 'api/path_test/nyaloka/';

  public authenticated: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public currentUser: UserDto = {username: '', firstName: ''};

  constructor(private httpClient: HttpClient, private logger: NGXLogger) {
    this.init();
    this.authenticated.subscribe(data => logger.debug('Authenticated: ', data));
  }

  private init() {
    this.httpClient
      .get<UserDto>(this.authUrl)
      .subscribe(
        data => {
          this.currentUser = data;
          this.authenticated.next(true);
        },
        error => {
          console.log('srv msg:', error.error);
        }
      );
  }

  login(credentials: LoginDto) {
    this.httpClient
      .post<UserDto>(this.authUrl, credentials)
      .subscribe(
        data => {
          this.currentUser = data;
          this.authenticated.next(true);
          console.log('Login success', data);
          return;
        },
        error => {
          this.authenticated.next(false);
          console.log('srv msg:', error.error);
        }
      );
  }

  logout() {

  }

  test() {

    // this.httpClient.get(this.testUrl).subscribe(cucc => console.log(cucc));
    this.httpClient.post(this.testUrl, '').subscribe(cucc => console.log(cucc));
  }
}

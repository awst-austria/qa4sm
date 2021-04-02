import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, Observable, of, Subject} from 'rxjs';
import {LoginDto} from './login.dto';
import {NGXLogger} from 'ngx-logger';
import {UserDto} from './user.dto';
import {catchError, map} from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = environment.API_URL;

  private loginUrl = this.API_URL + 'api/auth/login';
  private logoutUrl = this.API_URL + 'api/auth/logout';

  public authenticated: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public currentUser: UserDto = {username: '', firstName: ''};

  constructor(private httpClient: HttpClient, private logger: NGXLogger) {
    this.init();
  }

  private init() {
    this.httpClient
      .get<UserDto>(this.loginUrl)
      .subscribe(
        data => {
          this.currentUser = data;
          this.authenticated.next(true);
        },
        error => {

        }
      );
  }

  public isAuthenticated(): Observable<boolean> {
    return this.httpClient
      .get<UserDto>(this.loginUrl).pipe(map(user => {
        if (user != null) {
          return true;
        }
        return false;
      }), catchError(error => of(false)));
  }

  login(credentials: LoginDto): Subject<boolean> {
    let authResult = new Subject<boolean>();
    this.httpClient
      .post<UserDto>(this.loginUrl, credentials)
      .subscribe(
        data => {
          this.currentUser = {username: '', firstName: ''};
          this.authenticated.next(true);
          authResult.next(true);
        },
        error => {
          this.authenticated.next(false);
          authResult.next(false);
        }
      );

    return authResult;
  }

  logout(): Subject<boolean> {
    let logoutResult = new Subject<boolean>();
    this.httpClient
      .post(this.logoutUrl, null)
      .subscribe(
        data => {
          this.currentUser = {username: '', firstName: ''};
          this.authenticated.next(false);
          logoutResult.next(true);
        },
        error => {
          logoutResult.next(false);
        }
      );
    return logoutResult;
  }

}

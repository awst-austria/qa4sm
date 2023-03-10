import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, Observable, of, Subject} from 'rxjs';
import {LoginDto} from './login.dto';
import {UserDto} from './user.dto';
import {catchError, map} from 'rxjs/operators';

// const csrfToken = '{{csrf_token}}';
// const headers = new HttpHeaders({'X-CSRFToken': csrfToken});
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = environment.API_URL;

  private loginUrl = this.API_URL + 'api/auth/login';
  private logoutUrl = this.API_URL + 'api/auth/logout';
  private signUpUrl = this.API_URL + 'api/sign-up';
  private userUpdateUrl = this.API_URL + 'api/user-update';
  private userDeleteUrl = this.API_URL + 'api/user-delete';
  private passwordResetUrl = this.API_URL + 'api/password-reset';
  private setPasswordUrl = this.API_URL + 'api/password-resetconfirm';
  private validateTokenUrl = this.API_URL + 'api/password-resetvalidate_token/';

  emptyUser = {
    username: '',
    first_name: '',
    id: null,
    copied_runs: [],
    email: '',
    last_name: '',
    organisation: '',
    country: '',
    orcid: '',
    space_limit: '',
    space_limit_value: null,
    space_left: null
  };
  public authenticated: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public currentUser: UserDto = this.emptyUser;
  private passwordResetToken: BehaviorSubject<string> = new BehaviorSubject<string>('');
  private previousUrl: BehaviorSubject<string> = new BehaviorSubject<string>('');

  constructor(private httpClient: HttpClient) {
    this.init();
  }

  public init() {
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
          this.currentUser = data;
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
          this.currentUser = this.emptyUser;
          this.authenticated.next(false);
          logoutResult.next(true);
        },
        error => {
          logoutResult.next(false);
        }
      );
    return logoutResult;
  }

  signUp(userForm: any): Observable<any> {
    return this.httpClient.post(this.signUpUrl, userForm, {observe: 'body', responseType: 'json'});
  }

  updateUser(userForm: any): Observable<any> {
    return this.httpClient.patch(this.userUpdateUrl, userForm);
  }

  deactivateUser(username: any): Observable<any> {
    return this.httpClient.delete<UserDto>(this.userDeleteUrl, username);
  }

  resetPassword(resetPasswordForm: any): Observable<any> {
    return this.httpClient.post(this.passwordResetUrl, resetPasswordForm);
  }

  setPassword(setPasswordForm: any, token: string): Observable<any> {
    const setPasswordUrlWithToken = this.setPasswordUrl + '/?token=' + token;
    return this.httpClient.post(setPasswordUrlWithToken, setPasswordForm);
  }

  validateResetPasswordToken(tkn: string): Observable<any> {
    return this.httpClient.post(this.validateTokenUrl, {token: tkn});
  }

  checkPasswordResetToken(): Observable<string> {
    return this.passwordResetToken.asObservable();
  }

  setPasswordResetToken(newToken: string): void {
    this.passwordResetToken.next(newToken);
  }

  checkPreviousUrl(): Observable<string>{
    return this.previousUrl.asObservable();
  }

  setPreviousUrl(prevUrl: string): void{
    this.previousUrl.next(prevUrl);
  }
}

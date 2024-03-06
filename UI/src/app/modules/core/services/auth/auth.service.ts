import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, Observable, of, Subject} from 'rxjs';
import {LoginDto} from './login.dto';
import {UserDto} from './user.dto';
import {catchError, map} from 'rxjs/operators';
import {HttpErrorService} from '../global/http-error.service';

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
  private contactUrl = this.API_URL + 'api/support-request';

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
    space_left: null,
    is_staff: false,
    is_superuser: false
  };
  public authenticated$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public currentUser: UserDto = this.emptyUser;
  private passwordResetToken: BehaviorSubject<string> = new BehaviorSubject<string>('');
  private previousUrl: BehaviorSubject<string> = new BehaviorSubject<string>('');

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
    this.init();
  }

  public init() {
    this.httpClient
      .get<UserDto>(this.loginUrl)
      .subscribe(
        data => {
          this.currentUser = data;
          this.authenticated$.next(true);
        }
      );
  }

  public isAuthenticated(): Observable<boolean> {
    return this.httpClient
      .get<UserDto>(this.loginUrl).pipe(map(user => {
        return user != null;
      }), catchError(error => of(false)));
  }

  login(credentials: LoginDto): Subject<boolean> {
    let authResult = new Subject<boolean>();
    const loginObserver = {
      next: data => this.onLoginNext(data, authResult),
      error: error => this.onLoginError(error, authResult)
    }
    this.httpClient
      .post<UserDto>(this.loginUrl, credentials)
      .subscribe(loginObserver);
    return authResult;
  }

  private onLoginNext(data, authResult): void {
    this.currentUser = data;
    this.authenticated$.next(true);
    authResult.next(true);
  }

  private onLoginError(error, authResult): void {
    this.authenticated$.next(false);
    authResult.next(false);
  }

  logout(): Subject<boolean> {
    let logoutResult = new Subject<boolean>();
    const logoutObserver = {
      next: data => this.onLogoutNext(data, logoutResult),
      error: () => this.onLogoutError(logoutResult)
    }
    this.httpClient
      .post(this.logoutUrl, null)
      .subscribe(logoutObserver);

    return logoutResult;
  }

  private onLogoutNext(data, logoutResult): void {
    this.currentUser = this.emptyUser;
    this.authenticated$.next(false);
    logoutResult.next(true);
  }

  private onLogoutError(logoutResult): void {
    logoutResult.next(false);
  }


  signUp(userForm: any): Observable<any> {
    return this.httpClient.post(this.signUpUrl, userForm, {observe: 'body', responseType: 'json'})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  updateUser(userForm: any): Observable<any> {
    return this.httpClient.patch(this.userUpdateUrl, userForm)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  deactivateUser(username: any): Observable<any> {
    return this.httpClient.delete<UserDto>(this.userDeleteUrl, username)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  resetPassword(resetPasswordForm: any): Observable<any> {
    return this.httpClient.post(this.passwordResetUrl, resetPasswordForm)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  setPassword(setPasswordForm: any, token: string): Observable<any> {
    const setPasswordUrlWithToken = this.setPasswordUrl + '/?token=' + token;
    return this.httpClient.post(setPasswordUrlWithToken, setPasswordForm)
      .pipe(
      catchError(err => this.httpError.handleError(err))
    );
  }

  validateResetPasswordToken(tkn: string): Observable<any> {
    return this.httpClient.post(this.validateTokenUrl, {token: tkn})
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

  checkPasswordResetToken(): Observable<string> {
    return this.passwordResetToken.asObservable();
  }

  setPasswordResetToken(newToken: string): void {
    this.passwordResetToken.next(newToken);
  }

  checkPreviousUrl(): Observable<string> {
    return this.previousUrl.asObservable();
  }

  setPreviousUrl(prevUrl: string): void {
    this.previousUrl.next(prevUrl);
  }

  sendSupportRequest(messageForm): Observable<any> {
    return this.httpClient.post(this.contactUrl, messageForm)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

}

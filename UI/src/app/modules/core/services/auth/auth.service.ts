import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, EMPTY, Observable, of, Subject} from 'rxjs';
import {LoginDto} from './login.dto';
import {UserDto} from './user.dto';
import {catchError, map} from 'rxjs/operators';
import {HttpErrorService} from '../global/http-error.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = environment.API_URL;
  
  private emailURL = this.API_URL + 'api/auth/check-email';
  private loginUrl = this.API_URL + 'api/auth/login';
  private logoutUrl = this.API_URL + 'api/auth/logout';
  private signUpUrl = this.API_URL + 'api/sign-up';
  private userUpdateUrl = this.API_URL + 'api/user-update';
  private userDeleteUrl = this.API_URL + 'api/user-delete';
  private passwordResetUrl = this.API_URL + 'api/password-reset/';
  private setPasswordUrl = this.API_URL + 'api/password-reset/confirm';
  private validateTokenUrl = this.API_URL + 'api/password-reset/validate_token/';
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
  public authenticated: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public currentUser: UserDto = this.emptyUser;



  private passwordResetTokenSubject: BehaviorSubject<string> = new BehaviorSubject<string>('');
  passwordResetToken$: Observable<string> = this.passwordResetTokenSubject.asObservable();

  private previousUrlSubject: BehaviorSubject<string> = new BehaviorSubject<string>('');
  previousUrl$: Observable<string> = this.previousUrlSubject.asObservable();

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService) {
    this.init();
  }

  // todo: check if this method is actually needed
  public init() {
    this.httpClient.get<UserDto>(this.loginUrl)
      .subscribe(
        data => {
          this.currentUser = data;
          this.authenticated.next(true);
        }
      );
  }

  public isAuthenticated(): Observable<boolean> {
    return this.httpClient
      .get<UserDto>(this.loginUrl)
      .pipe(
        map(user =>  user != null),
        catchError(error => of(false)));
  }

  // todo: remove subscription from the service
  login(credentials: LoginDto): Subject<boolean> {
    let authResult = new Subject<boolean>();
    this.httpClient
      .post<UserDto>(this.loginUrl, credentials)
      .pipe(
        catchError(error => this.onLoginError(error, authResult) )
      )
      .subscribe(data => this.onLoginNext(data, authResult));
    return authResult;
  }

  private onLoginNext(data, authResult): void {
    this.currentUser = data;
    this.authenticated.next(true);
    authResult.next(true);
  }

  private onLoginError(error, authResult): Observable<never> {
    this.authenticated.next(false);
    authResult.next(false);
    return EMPTY
  }
 // todo: remove subscription from the service
  logout(): Subject<boolean> {
    let logoutResult = new Subject<boolean>();
    this.httpClient
      .post(this.logoutUrl, null)
      .pipe(
        catchError(() => this.onLogoutError(logoutResult))
      )
      .subscribe(data => this.onLogoutNext(data, logoutResult));

    return logoutResult;
  }

  private onLogoutNext(data, logoutResult): void {
    this.currentUser = this.emptyUser;
    this.authenticated.next(false);
    logoutResult.next(true);
  }

  private onLogoutError(logoutResult): Observable<never> {
    logoutResult.next(false);
    return EMPTY
  }

  signUp(userForm: any): Observable<any> {
    return this.httpClient.post(this.signUpUrl, userForm, {observe: 'body', responseType: 'json'})
      .pipe(
        catchError(err => this.httpError.handleUserFormError(err))
      );
  }

  // Check that the provided email address is unique, avoid duplicate email addresses on different accounts
  checkUniqueEmail(email: string): Observable<boolean> {
    const encodedEmail = encodeURIComponent(email);
    return this.httpClient.get(`${this.emailURL}/${encodedEmail}`, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      responseType: 'text'
    }).pipe(
      map(response => {
        return response === 'true';
      }),
      catchError(error => {
        return of(false);
      })
    );
  }

  updateUser(userForm: any): Observable<any> {
    return this.httpClient.patch(this.userUpdateUrl, userForm)
      .pipe(
        catchError(err => this.httpError.handleUserFormError(err))
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
        catchError(err =>
          this.httpError.handleResetPasswordError(err, 'passwordReset')
        )
      );
  }

  setPassword(setPasswordForm: any, token: string): Observable<any> {
    const setPasswordUrlWithToken = this.setPasswordUrl + '/?token=' + token;
    return this.httpClient.post(setPasswordUrlWithToken, setPasswordForm)
      .pipe(
        catchError(err => this.httpError.handleResetPasswordError(err, 'settingPassword'))
      );
  }

  validateResetPasswordToken(tkn: string): Observable<any> {
    return this.httpClient.post(this.validateTokenUrl, {token: tkn})
      .pipe(
        catchError(err => this.httpError.handleResetPasswordError(err, 'tokenValidation'))
      );
  }

  setPasswordResetToken(newToken: string): void {
    this.passwordResetTokenSubject.next(newToken);
  }

  setPreviousUrl(prevUrl: string): void {
    this.previousUrlSubject.next(prevUrl);
  }

  sendSupportRequest(messageForm): Observable<any> {
    return this.httpClient.post(this.contactUrl, messageForm)
      .pipe(
        catchError(err => this.httpError.handleError(err))
      );
  }

}

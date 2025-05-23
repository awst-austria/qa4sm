import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, EMPTY, Observable, of, Subject, throwError} from 'rxjs';
import {LoginDto} from './login.dto';
import {UserDto} from './user.dto';
import {catchError, map, tap} from 'rxjs/operators';
import {HttpErrorService} from '../global/http-error.service';
import {Router, Routes} from '@angular/router';

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
  private passwordResetUrl = this.API_URL + 'api/password-reset/';
  private passwordUpdateUrl = this.API_URL + 'api/password-update';
  private setPasswordUrl = this.API_URL + 'api/password-reset/confirm';
  private validateTokenUrl = this.API_URL + 'api/password-reset/validate_token/';
  private contactUrl = this.API_URL + 'api/support-request';
  
  private apiTokenURL = this.API_URL + 'api/request-api-token';

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

  private unprotectedRoutes: string[] = [];

  private showLoginModalSubject = new BehaviorSubject<{show: boolean, message?: string}>({show: false});
  showLoginModal$ = this.showLoginModalSubject.asObservable();

  private passwordResetTokenSubject: BehaviorSubject<string> = new BehaviorSubject<string>('');
  passwordResetToken$: Observable<string> = this.passwordResetTokenSubject.asObservable();

  private previousUrlSubject: BehaviorSubject<string> = new BehaviorSubject<string>('');
  previousUrl$: Observable<string> = this.previousUrlSubject.asObservable();

  constructor(private httpClient: HttpClient,
              private httpError: HttpErrorService,
              private router: Router) {
    this.init();
    this.initializeUnprotectedRoutes();

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

  private initializeUnprotectedRoutes() {
    //Initialise the list of the unprotected routes from the router
    const routes: Routes = this.router.config;
    this.unprotectedRoutes = this.getUnprotectedRoutes(routes);
  }

  private getUnprotectedRoutes(routes: Routes): string[] {
    //Get unprotected routes from the router 
    const unprotectedRoutes = [];

    routes.forEach(route => {
      if ((!route.canActivate) && (route.path.length > 0)) {
        unprotectedRoutes.push(route.path);
      }
    })

    return unprotectedRoutes;
  }

  private isProtectedRoute(route: string): boolean {
    // Actually check if the provided route is in the list of unprotected routes - if not, it is assumed to be a protected route 
    // (safer approach that assumes all routes are protected unless specified)
    return !this.unprotectedRoutes.some(unprotectedRoute => (route.startsWith(unprotectedRoute, 1) && (unprotectedRoute.length > 0)));
  }

  public isAuthenticated(): Observable<boolean> {
    return this.httpClient
      .get<UserDto>(this.loginUrl)
      .pipe(
        map(user =>  user != null),
        catchError(error => of(false)));
  }

  switchLoginModal(switchOn: boolean, message: string | null = null) {
    // Toggle the login modal window with an optional header message
    this.showLoginModalSubject.next({show: switchOn, message});
  }

  login(credentials: LoginDto): Observable<UserDto> {
    // Log user in and redirect to home if on signup or password-reset page
    const currentRoute = this.router.url;
    return this.httpClient
      .post<UserDto>(this.loginUrl, credentials)
      .pipe(
        tap(user => {
          this.currentUser = user;
          this.authenticated.next(true);
          if ((currentRoute.startsWith('signup', 1)) || (currentRoute.startsWith('password-reset', 1))) {
            this.router.navigate(['/home']); 
          }
        }),
        catchError(error=> {
          this.authenticated.next(false);
          return throwError(() => error);
        })
      )
  }

  logout(): Observable<boolean> {
    // Log user out and redirect to home page if currently on a protected route
    const currentRoute = this.router.url;
    return this.httpClient
      .post(this.logoutUrl, null)
      .pipe(
        map(() => {
          this.currentUser = this.emptyUser; 
          this.authenticated.next(false);
          if (this.isProtectedRoute(currentRoute)) {
            this.router.navigate(['/home']); 
          }
          return true;
        }),
        catchError(() => {
          return of(false)
        })
      );
  }

  signUp(userForm: any): Observable<any> {
    return this.httpClient.post(this.signUpUrl, userForm, {observe: 'body', responseType: 'json'})
      .pipe(
        catchError(err => this.httpError.handleUserFormError(err))
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

  resetPasswordRequest(resetPasswordForm: any): Observable<any> {
    return this.httpClient.post(this.passwordResetUrl, resetPasswordForm)
      .pipe(
        catchError(err =>
          this.httpError.handleResetPasswordError(err, 'passwordReset')
        )
      );
  }

  resetPassword(setPasswordForm: any, token: string): Observable<any> {
    const setPasswordUrlWithToken = this.setPasswordUrl + '/?token=' + token;
    return this.httpClient.post(setPasswordUrlWithToken, setPasswordForm)
      .pipe(
        catchError(err => this.httpError.handleResetPasswordError(err, 'settingPassword'))
      );
  }

  updatePassword(setPasswordForm: any): Observable<any> {
    return this.httpClient.post(this.passwordUpdateUrl, setPasswordForm)
      .pipe(
        catchError(err => this.httpError.handleError(err, err.error.error))
      );
  }

  requestApiToken(): Observable<any> {
    return this.httpClient.post(this.apiTokenURL, {});
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

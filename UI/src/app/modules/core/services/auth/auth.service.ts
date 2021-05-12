import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from '../../../../../environments/environment';
import {BehaviorSubject, Observable, of, Subject} from 'rxjs';
import {LoginDto} from './login.dto';
import {NGXLogger} from 'ngx-logger';
import {UserDto} from './user.dto';
import {catchError, map} from 'rxjs/operators';

const csrfToken = '{{csrf_token}}';
const headers = new HttpHeaders({'X-CSRFToken': csrfToken});
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = environment.API_URL;

  private loginUrl = this.API_URL + 'api/auth/login';
  private logoutUrl = this.API_URL + 'api/auth/logout';
  private signUpUrl = this.API_URL + 'api/sign-up';

  emptyUser = {username: '',
    first_name: '',
    id: null,
    copied_runs: [],
    email: '',
    last_name: '',
    organisation: '',
    country: '',
    orcid: ''};
  public authenticated: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public currentUser: UserDto = this.emptyUser;

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
          this.currentUser = this.emptyUser;
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

  signUp(userForm: any): void{
    this.httpClient.post(this.signUpUrl, userForm, {headers, observe: 'body', responseType: 'text'}).subscribe(
      response => {
         console.log(response);
      });
  }
  // addValidation(validationId: string): void {
  //   const addUrl = resultUrl.replace('00000000-0000-0000-0000-000000000000', validationId);
  //   const data = {add_validation: true};
  //   this.httpClient.post(addUrl + '/', data, {headers, observe: 'body', responseType: 'text'}).subscribe(
  //     response => {
  //       alert(response);
  //     }
  //   );
  // }
  //


}

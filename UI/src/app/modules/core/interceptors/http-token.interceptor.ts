import {Injectable} from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor, HttpHeaders
} from '@angular/common/http';
import {Observable} from 'rxjs';
import {NGXLogger} from 'ngx-logger';

@Injectable()
export class HttpTokenInterceptor implements HttpInterceptor {
  constructor(private logger:NGXLogger) {
  }

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {

    let csrfToken = this.getCookie('csrftoken');
    if (csrfToken) {
      const authReq = request.clone({
        headers: request.headers
          .set('Content-Type', 'application/json')
          .set('X-CSRFToken', csrfToken)
      });
      return next.handle(authReq);
    }

    return next.handle(request);
  }

  private getCookie(name: string) {
    let ca: Array<string> = document.cookie.split(';');
    let caLen: number = ca.length;
    let cookieName = `${name}=`;
    let c: string;

    for (let i: number = 0; i < caLen; i += 1) {
      c = ca[i].replace(/^\s+/g, '');
      if (c.indexOf(cookieName) == 0) {
        return c.substring(cookieName.length, c.length);
      }
    }
    return null;
  }
}

import {Injectable} from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor, HttpHeaders
} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable()
export class HttpTokenInterceptor implements HttpInterceptor {
  constructor() {
  }

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {

    let csrfToken = this.getCookie('csrftoken');
    if (csrfToken) {
      console.log()
      const authReq = request.clone({setHeaders: {'X-CSRFToken': csrfToken}});
      console.info(authReq);

      next.handle(authReq);
    }


    return next.handle(request);

  }

  private getCookie(name: string) {
    let ca: Array<string> = document.cookie.split(';');
    let caLen: number = ca.length;
    let cookieName = `${name}=`;
    let c: string;

    console.log(ca);
    for (let i: number = 0; i < caLen; i += 1) {
      c = ca[i].replace(/^\s+/g, '');
      if (c.indexOf(cookieName) == 0) {
        return c.substring(cookieName.length, c.length);
      }
    }
    return null;
  }
}

import {Injectable} from '@angular/core';
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {Observable} from 'rxjs';
import {ModalWindowService} from '../services/global/modal-window.service';
import {finalize} from 'rxjs/operators';

@Injectable()
export class LoadingInterceptor implements HttpInterceptor {

  constructor(private modalWindowService: ModalWindowService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    this.modalWindowService.open();
    return next.handle(request).pipe(
      finalize(() => {
        this.modalWindowService.close();
      })
    );
  }
}

import {Injectable} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HttpErrorService {

  constructor() { }


  private customHttpErrorFormatter(err: HttpErrorResponse): CustomHttpError {
    let errorMessage = '';
    if (err.error instanceof ErrorEvent) {
      console.error(`Client-side or network problem ${err.error.message}.`)
      errorMessage = `An error occurred: ${err.error.message}`;
    } else {
      console.error(`Problem on the server side. Server returned code: ${err.status}.
      Error message is: ${err.statusText}`)
      errorMessage = `${err.error.message ? err.error.message : err.statusText}`;
    }
    return {status: err.status, message: errorMessage};
  }

  handleError(error: HttpErrorResponse): Observable<never>{
    return throwError(() => this.customHttpErrorFormatter(error))
  }


}

interface CustomHttpError {
  status: number,
  message: string
}

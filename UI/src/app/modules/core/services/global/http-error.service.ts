import {Injectable} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HttpErrorService {

  constructor() {
  }


  private customHttpErrorFormatter(err: HttpErrorResponse,
                                   message: string | undefined,
                                   header: string | undefined): CustomHttpError {

    /**
     * Error status doesn't tell much to the user, therefore we take either a message passed when piping particular
     * request or from the error message, if it's passed from the backend. If none exists, we pass undefined and the
     *  message will be defined separately in each case
     */

    let errorMessage = undefined;
    const errorHeader = header ? header : 'Something went wrong'

    if (err.error instanceof ErrorEvent) {
      console.error(`Client-side or network problem ${err.error.message}.`)
      errorMessage = message ? message : `An error occurred: ${err.error.message}`;
    } else {
      console.error(`Problem on the server side. Server returned code: ${err.status}.
      Error message is: ${err.statusText}`)
        errorMessage = message ? message : `${err.error.message ? err.error.message : undefined}`;
    }
    return {status: err.status, message: errorMessage, header: errorHeader};
  }

  handleError(error: HttpErrorResponse,
              message: string | undefined = undefined,
              header: string | undefined = undefined): Observable<never> {
    return throwError(() => this.customHttpErrorFormatter(error, message, header))
  }


}

export interface CustomHttpError {
  status: number,
  message: string,
  header?: string,
}

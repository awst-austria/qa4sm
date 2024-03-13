import {Injectable} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HttpErrorService {

  constructor() {
  }

  somethingWentWrongPhrase = 'Something went wrong';

  restPasswordErrorsMessages = {
    tokenValidation: (error: PasswordResetError) => this.getMessageForTokenValidation(error), // token validation
    settingPassword: (error: PasswordResetError) => this.getMessageForSettingPassword(error), // setting password
    passwordReset: (error: PasswordResetError) => this.getMessageForPasswordReset(error) // password reset
  }

  private clientSideErrorFormatter(error: HttpErrorResponse): CustomHttpError {
    console.error(`Client-side or network problem ${error.error.message}.`)
    return {
      status: error.status, errorMessage: {
        message: `An error occurred: ${error.error.message}`,
        header: undefined
      }
    };
  }

  private serverSideErrorFormatter(error: HttpErrorResponse,
                                   message: string | undefined,
                                   header: string | undefined): CustomHttpError {
    console.error(
      `Problem on the server side. Server returned code: ${error.status}. Error message is: ${error.statusText}`
    )
    const errorHeader = header ? header : this.somethingWentWrongPhrase
    const errorMessage = message ? message : `${error.error.message ? error.error.message : undefined}`;
    return {status: error.status, errorMessage: {message: errorMessage, header: errorHeader}};
  }

  private customHttpErrorFormatter(error: HttpErrorResponse,
                                   message: string | undefined,
                                   header: string | undefined): CustomHttpError {

    if (error.error instanceof ErrorEvent) {
      return this.clientSideErrorFormatter(error)
    } else {
      return this.serverSideErrorFormatter(error, message, header)
    }
  }

  private resetPasswordHttpErrorsFormatter(error: HttpErrorResponse,
                                           key: string): CustomHttpError{
    if (error.error instanceof ErrorEvent) {
      return this.clientSideErrorFormatter(error)
    } else {
      return {status: error.status, errorMessage: this.restPasswordErrorsMessages[key](error.error)};
    }
  }

  handleError(error: HttpErrorResponse,
              message: string | undefined = undefined,
              header: string | undefined = undefined): Observable<never> {
    return throwError(() => this.customHttpErrorFormatter(error, message, header))
  }

  handleResetPasswordError(error: HttpErrorResponse,
                           key: string): Observable<never> {
    return throwError(() => this.resetPasswordHttpErrorsFormatter(error, key))
  }


  getMessageForTokenValidation(error: PasswordResetError): ErrorMessage {
    const message: string = error.detail
      ? "Possibly the link has been already used. Please request a new password reset." :
      'Setting new password is currently not possible. Please try again later or contact our support team.';
    const header: string = error.detail ? 'Invalid password reset link' : this.somethingWentWrongPhrase
    return {message: message, header: header}
  }

  getMessageForPasswordReset(error: PasswordResetError): ErrorMessage{
    const message: string = error.email ? error.email[0]
      : 'We could not reset your password. Please try again in a few minutes or contact us using our contact form.'
    const header: string = error.email ? 'Invalid email address' : this.somethingWentWrongPhrase

    console.log(error.email)
    return {message: message, header: header}
  }

  getMessageForSettingPassword(error: PasswordResetError): ErrorMessage{
    return {message: '', header: ''}
  }

}

export interface CustomHttpError {
  status: number,
  errorMessage: ErrorMessage
}

interface ErrorMessage {
  message: string,
  header?: string,
}

interface PasswordResetError{
  detail: string[],
  email: string[],
  password: string[],
  token: string[]
}





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
  defaultMessage = `If the error persist please contact our support team.`

  private clientSideErrorFormatter(error: HttpErrorResponse): CustomHttpError {
    console.error(`Client-side or network problem ${error.error.message}.`)
    return {
      status: error.status,
      errorMessage: {
        message: `An error occurred: ${error.error.message}`,
        header: undefined,
      },
      form: undefined
    };
  }

  private serverSideErrorFormatter(error: HttpErrorResponse,
                                   message: string | undefined,
                                   header: string | undefined): CustomHttpError {
    console.error(
      `Problem on the server side. Server returned code: ${error.status}. Error message is: ${error.statusText}`
    );
    const errorHeader = header ? header : this.somethingWentWrongPhrase;
    const errorMessage = message ? message + this.defaultMessage : this.defaultMessage;
    const errorForm = typeof error.error === 'object' ? error.error : undefined;
    return {status: error.status, errorMessage: {message: errorMessage, header: errorHeader}, form: errorForm};
  }


  // this error formatter returns an object with error status, error form if exists, and error message as header and
  // the message text. The message and header text can be passed to be included, otherwise it is going to be a default
  // phrase.
  private customHttpErrorFormatter(error: HttpErrorResponse,
                                   message: string | undefined,
                                   header: string | undefined): CustomHttpError {

    if (error.error instanceof ErrorEvent) {
      return this.clientSideErrorFormatter(error);
    } else {
      return this.serverSideErrorFormatter(error, message, header);
    }
  }

  private resetPasswordHttpErrorsFormatter(error: HttpErrorResponse,
                                           key: string): CustomHttpError{
    if (error.error instanceof ErrorEvent) {
      return this.clientSideErrorFormatter(error);
    } else {
      return {status: error.status, errorMessage: this.restPasswordErrorsMessages[key](error.error)};
    }
  }

  handleError(error: HttpErrorResponse,
              message: string | undefined = undefined,
              header: string | undefined = undefined): Observable<never> {
    return throwError(() => this.customHttpErrorFormatter(error, message, header));
  }

  handleUserFormError(error: HttpErrorResponse): Observable<never>{
    let errorMessage = 'We could not submit your form. Please try again later or contact our support team.';
    let errorHeader = 'Something went wrong.'

    if (typeof error.error === 'object'){
      errorMessage = 'Please review your input and ensure all fields are correctly filled out.';
      errorHeader = 'Invalid user data'
    }

    return throwError(() => this.customHttpErrorFormatter(error, errorMessage, errorHeader));
  }

  handleResetPasswordError(error: HttpErrorResponse,
                           key: string): Observable<never> {
    return throwError(() => this.resetPasswordHttpErrorsFormatter(error, key));
  }

  /**
   * Below are functions that return messages to handle errors related to the password reset. Normally I'd rather
   * pass the message from the backend, but for this purpose we are using a separate package, and we have no impact on
   * the error message. Therefore, we need to handle it here
   */

  private restPasswordErrorsMessages = {
    tokenValidation: (error: PasswordResetError) => this.getMessageForTokenValidation(error),
    settingPassword: (error: PasswordResetError) => this.getMessageForSettingPassword(error),
    passwordReset: (error: PasswordResetError) => this.getMessageForPasswordReset(error)
  };

  private getMessageForTokenValidation(error: PasswordResetError): ErrorMessage {
    const message: string = error.detail
      ? "Possibly the link has been already used. Please request a new password reset." :
      'Setting new password is currently not possible. Please try again later or contact our support team.';
    const header: string = error.detail ? 'Invalid password reset link' : this.somethingWentWrongPhrase;
    console.log(message, header)
    return {message: message, header: header};
  }

  private getMessageForPasswordReset(error: PasswordResetError): ErrorMessage{
    const message: string = error.email ? error.email[0]
      : 'We could not reset your password. Please try again in a few minutes or contact us using our contact form.';
    const header: string = error.email ? 'Invalid email address' : this.somethingWentWrongPhrase;

    return {message: message, header: header};
  }

  private getMessageForSettingPassword(error: PasswordResetError): ErrorMessage{
    let message = '';
    let header = undefined;
    if (error.token) {
      message = 'To get the password reset token, you need to request reset your password using our form. ' +
        'If that does not work, contact us to get help.';
      header = 'Invalid password reset token';
    } else if (error.password){
      error.password.forEach(msg => message += `${msg}\n`);
      header = 'Invalid password';
    } else {
      message = 'We could not set your password. Please try again later or contact our support team. '
      header = this.somethingWentWrongPhrase;
    }

    return {message: message, header: header};
  }

}

export interface CustomHttpError {
  status: number,
  errorMessage: ErrorMessage
  form? : object | undefined,
}

interface ErrorMessage {
  message?: string,
  header?: string,
}

interface PasswordResetError{
  detail: string[],
  email: string[],
  password: string[],
  token: string[]
}





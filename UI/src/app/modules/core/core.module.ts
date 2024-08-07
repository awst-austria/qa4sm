import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from './services/auth/auth.service';
import {HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import {HttpTokenInterceptor} from './interceptors/http-token.interceptor';
import {BrowserModule} from '@angular/platform-browser';
import {LoadingSpinnerComponent} from './tools/loading-spinner/loading-spinner.component';
import {ErrorComponent} from './error/error.component';


@NgModule({ declarations: [LoadingSpinnerComponent, ErrorComponent],
    exports: [
        LoadingSpinnerComponent,
        ErrorComponent
    ], imports: [BrowserModule,
        CommonModule], providers: [
        AuthService,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: HttpTokenInterceptor,
            multi: true
        },
        provideHttpClient(withInterceptorsFromDi()),
    ] })
export class CoreModule {
}

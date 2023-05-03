import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from './services/auth/auth.service';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {HttpTokenInterceptor} from './interceptors/http-token.interceptor';
import {BrowserModule} from '@angular/platform-browser';
import {LoadingSpinnerComponent} from './tools/loading-spinner/loading-spinner.component';


@NgModule({
    declarations: [LoadingSpinnerComponent],
    imports: [
        BrowserModule,
        CommonModule,
        HttpClientModule
    ],
  exports: [
    LoadingSpinnerComponent
  ],
    providers: [
        AuthService,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: HttpTokenInterceptor,
            multi: true
        },
    ]
})
export class CoreModule {
}

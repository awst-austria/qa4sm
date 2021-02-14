import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {MenubarModule} from 'primeng/menubar';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {FormsModule} from '@angular/forms';
import {NavigationBarModule} from './modules/navigation-bar/navigation-bar.module';
import {CarouselModule} from 'primeng/carousel';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {GalleriaModule} from 'primeng/galleria';
import {ButtonModule} from 'primeng/button';
import {ErrorComponent} from './pages/error/error.component';
import {CardModule} from 'primeng/card';
import {ValidationsComponent} from './pages/validations/validations.component';
import {ValidationComponent} from './pages/validation/validation.component';
import {LoginComponent} from './pages/login/login.component';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {HttpTokenInterceptor} from './modules/core/interceptors/http-token.interceptor';
import {LoggerModule, NgxLoggerLevel} from 'ngx-logger';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ValidateComponent,
    ErrorComponent,
    ValidationsComponent,
    ValidationComponent,
    LoginComponent
  ],
  imports: [
    LoggerModule.forRoot({level: NgxLoggerLevel.DEBUG, serverLogLevel: NgxLoggerLevel.ERROR}),
    NavigationBarModule,
    FormsModule,
    BrowserModule,
    HttpClientModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    MenubarModule,
    CarouselModule,
    GalleriaModule,
    ButtonModule,
    CardModule

  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpTokenInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}

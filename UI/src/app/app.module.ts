import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {NavigationBarModule} from './modules/navigation-bar/navigation-bar.module';

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {ErrorComponent} from './pages/error/error.component';

import {ValidationsComponent} from './pages/validations/validations.component';
import {ValidationComponent} from './pages/validation/validation.component';
import {LoginComponent} from './pages/login/login.component';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {HttpTokenInterceptor} from './modules/core/interceptors/http-token.interceptor';
import {LoggerModule, NgxLoggerLevel} from 'ngx-logger';

import {UserProfileComponent} from './pages/user-profile/user-profile.component';

import {DatasetModule} from './modules/dataset/dataset.module';
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {DropdownModule} from 'primeng/dropdown';
import {PanelModule} from 'primeng/panel';
import {AccordionModule} from 'primeng/accordion';
import {TooltipModule} from 'primeng/tooltip';
import {ButtonModule} from 'primeng/button';
import {PasswordModule} from 'primeng/password';
import {InputTextModule} from 'primeng/inputtext';
import {FilterModule} from './modules/filter/filter.module';
import {ToastModule} from 'primeng/toast';
import {MessageService} from 'primeng/api';
import {PublishedValidationsComponent} from './pages/published-validations/published-validations.component';
import {ValidationResultModule} from './modules/validation-result/validation-result.module';
import {SpatialSubsetModule} from './modules/spatial-subset/spatial-subset.module';
import {CarouselModule} from 'primeng/carousel';
import {ValidationPeriodModule} from './modules/validation-period/validation-period.module';
import {MetricsModule} from './modules/metrics/metrics.module';
import {AnomaliesModule} from './modules/anomalies/anomalies.module';
import {ScalingModule} from './modules/scaling/scaling.module';
import {PaginatorModule} from 'primeng/paginator';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ValidateComponent,
    ErrorComponent,
    ValidationsComponent,
    ValidationComponent,
    LoginComponent,
    UserProfileComponent,
    PublishedValidationsComponent
  ],
  imports: [
    LoggerModule.forRoot({level: NgxLoggerLevel.DEBUG, serverLogLevel: NgxLoggerLevel.ERROR}),
    NavigationBarModule,
    FormsModule,
    ReactiveFormsModule,
    BrowserModule,
    HttpClientModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    DatasetModule,
    NgbModule,
    FontAwesomeModule,
    ToastModule,
    DropdownModule,
    AccordionModule,
    PanelModule,
    TooltipModule,
    ButtonModule,
    PasswordModule,
    InputTextModule,
    FilterModule,
    ToastModule,
    ValidationResultModule,
    SpatialSubsetModule,
    CarouselModule,
    ValidationPeriodModule,
    MetricsModule,
    AnomaliesModule,
    ScalingModule,
    PaginatorModule,

  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpTokenInterceptor,
      multi: true
    },
    MessageService
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}

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
import {ValidationResultComponent} from './pages/validation-result/validation-result.component';
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
import {NgxPaginationModule} from 'ngx-pagination';
import {MapModule} from './modules/map/map.module';
import {AboutComponent} from './pages/about/about.component';
import {TermsComponent} from './pages/terms/terms.component';
import {DatasetInfoComponent} from './pages/dataset-info/dataset-info.component';
import {ComparisonComponent} from './pages/comparison/comparison.component';
import {ComparisonModule} from './modules/comparison/comparison.module';
import {ValidationSelectorModule} from './modules/validation-selector/validation-selector.module'


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ValidateComponent,
    ErrorComponent,
    ValidationsComponent,
    ValidationResultComponent,
    LoginComponent,
    UserProfileComponent,
    PublishedValidationsComponent,
    AboutComponent,
    TermsComponent,
    DatasetInfoComponent,
    ComparisonComponent,
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
    NgxPaginationModule,
    MapModule,
    ComparisonModule,
    ValidationSelectorModule,

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

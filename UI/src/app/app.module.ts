import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './pages/home/home.component';
import { ValidateComponent } from './pages/validate/validate.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NavigationBarModule } from './modules/navigation-bar/navigation-bar.module';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { ErrorPageComponent } from './pages/error/error-page.component';

import { ValidationsComponent } from './pages/validations/validations.component';
import { ValidationResultComponent } from './pages/validation-result/validation-result.component';
import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { HttpTokenInterceptor } from './modules/core/interceptors/http-token.interceptor';
import { LoggerModule, NgxLoggerLevel } from 'ngx-logger';

import { UserProfileComponent } from './pages/user-profile/user-profile.component';

import { DatasetModule } from './modules/dataset/dataset.module';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { DropdownModule } from 'primeng/dropdown';
import { PanelModule } from 'primeng/panel';
import { AccordionModule } from 'primeng/accordion';
import { TooltipModule } from 'primeng/tooltip';
import { ButtonModule } from 'primeng/button';
import { PasswordModule } from 'primeng/password';
import { InputTextModule } from 'primeng/inputtext';
import { FilterModule } from './modules/filter/filter.module';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { PublishedValidationsComponent } from './pages/published-validations/published-validations.component';
import { ValidationResultModule } from './modules/validation-result/validation-result.module';
import { SpatialSubsetModule } from './modules/spatial-subset/spatial-subset.module';
import { CarouselModule } from 'primeng/carousel';
import { ValidationPeriodModule } from './modules/validation-period/validation-period.module';
import { MetricsModule } from './modules/metrics/metrics.module';
import { AnomaliesModule } from './modules/anomalies/anomalies.module';
import { ScalingModule } from './modules/scaling/scaling.module';
import { MapModule } from './modules/map/map.module';
import { TermsComponent } from './pages/terms/terms.component';
import { DatasetInfoComponent } from './pages/dataset-info/dataset-info.component';
import { ComparisonComponent } from './pages/comparison/comparison.component';
import { ComparisonModule } from './modules/comparison/comparison.module';
import {
  TemporalMatchingComponent
} from './modules/temporal-matching/components/temporal-matching/temporal-matching.component';
import { TemporalMatchingModule } from './modules/temporal-matching/temporal-matching.module';
import { HelpComponent } from './pages/help/help.component';
import { CoreModule } from './modules/core/core.module';
import { SignupComponent } from './pages/signup/signup.component';
import { UserModule } from './modules/user/user.module';
import { SignupCompleteComponent } from './pages/signup-complete/signup-complete.component';
import { DeactivateUserCompleteComponent } from './pages/deactivate-user-complete/deactivate-user-complete.component';
import { PasswordResetComponent } from './pages/password-reset/password-reset.component';
import { PasswordResetDoneComponent } from './pages/password-reset-done/password-reset-done.component';
import { SetPasswordComponent } from './pages/set-password/set-password.component';
import {
  PasswordResetValidateTokenComponent
} from './pages/password-reset-validate-token/password-reset-validate-token.component';
import { InputNumberModule } from 'primeng/inputnumber';
import { MyDatasetsComponent } from './pages/my-datasets/my-datasets.component';
import { UserDatasetsModule } from './modules/user-datasets/user-datasets.module';
import { ValidationReferenceModule } from './modules/validation-reference/validation-reference.module';
import { UserDataGuidelinesComponent } from './pages/user-data-guidelines/user-data-guidelines.component';
import { DialogModule } from 'primeng/dialog';
import { ProgressBarModule } from 'primeng/progressbar';
import { ImageModule } from 'primeng/image';
import { ScrollTopModule } from 'primeng/scrolltop';
import { ContactUsComponent } from './pages/contact-us/contact-us.component';
import { ContactModule } from './modules/contact/contact.module';
import { SelectButtonModule } from 'primeng/selectbutton';
import { MaintenanceModeComponent } from './modules/core/maintenance-mode/maintenance-mode.component';
import {
  InteractiveMapComponent
} from './modules/validation-result/components/interactive-map/interactive-map.component';

@NgModule({ declarations: [
        AppComponent,
        HomeComponent,
        ValidateComponent,
        ErrorPageComponent,
        ValidationsComponent,
        ValidationResultComponent,
        UserProfileComponent,
        PublishedValidationsComponent,
        TermsComponent,
        DatasetInfoComponent,
        ComparisonComponent,
        HelpComponent,
        SignupComponent,
        SignupCompleteComponent,
        DeactivateUserCompleteComponent,
        PasswordResetComponent,
        PasswordResetDoneComponent,
        SetPasswordComponent,
        PasswordResetValidateTokenComponent,
        TemporalMatchingComponent,
        MyDatasetsComponent,
        UserDataGuidelinesComponent,
        ContactUsComponent,
    ],
    bootstrap: [AppComponent],
    imports: [LoggerModule.forRoot({level: NgxLoggerLevel.DEBUG, serverLogLevel: NgxLoggerLevel.ERROR}),
        NavigationBarModule,
        FormsModule,
        ReactiveFormsModule,
        BrowserModule,
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
        TemporalMatchingModule,
        CarouselModule,
        ValidationPeriodModule,
        MetricsModule,
        AnomaliesModule,
        ScalingModule,
        MapModule,
        ComparisonModule,
        CoreModule,
        UserModule,
        InputNumberModule,
        UserDatasetsModule,
        ValidationReferenceModule,
        DialogModule,
        ProgressBarModule,
        ImageModule,
        ScrollTopModule,
        ContactModule,
        SelectButtonModule, MaintenanceModeComponent, InteractiveMapComponent], providers: [
        {
            provide: HTTP_INTERCEPTORS,
            useClass: HttpTokenInterceptor,
            multi: true
        },
        MessageService,
        provideHttpClient(withInterceptorsFromDi())
    ] })
export class AppModule {
}

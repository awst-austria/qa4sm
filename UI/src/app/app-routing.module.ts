import {NgModule} from '@angular/core';
import {ExtraOptions, RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {ErrorPageComponent} from './pages/error/error-page.component';
import {AuthGuard} from './auth.guard';
import {ValidationResultComponent} from './pages/validation-result/validation-result.component';
import {UserProfileComponent} from './pages/user-profile/user-profile.component';
import {PublishedValidationsComponent} from './pages/published-validations/published-validations.component';
import {ValidationsComponent} from './pages/validations/validations.component';
import {TermsComponent} from './pages/terms/terms.component';
import {DatasetInfoComponent} from './pages/dataset-info/dataset-info.component';
import {ComparisonComponent} from './pages/comparison/comparison.component';
import {HelpComponent} from './pages/help/help.component';
import {SignupComponent} from './pages/signup/signup.component';
import {SignupCompleteComponent} from './pages/signup-complete/signup-complete.component';
import {DeactivateUserCompleteComponent} from './pages/deactivate-user-complete/deactivate-user-complete.component';
import {DatasetResolver} from './modules/core/services/dataset/dataset.resolver';
import {PasswordResetComponent} from './pages/password-reset/password-reset.component';
import {PasswordResetDoneComponent} from './pages/password-reset-done/password-reset-done.component';
import {SetPasswordComponent} from './pages/set-password/set-password.component';
import {PasswordResetValidateTokenComponent} from './pages/password-reset-validate-token/password-reset-validate-token.component';
import {MyDatasetsComponent} from './pages/my-datasets/my-datasets.component';
import { UserDataGuidelinesComponent2 } from './pages/user-data-guidelines2/user-data-guidelines2.component';
import {UserDataGuidelinesComponent} from './pages/user-data-guidelines/user-data-guidelines.component';
import {ContactUsComponent} from './pages/contact-us/contact-us.component';
import { PublicApiComponent } from './pages/public-api/public-api.component';
import { JsonConfigComponent } from './pages/public-api/json-config/json-config.component';
import { CustomisePlotsComponent } from './pages/customise-plots/customise-plots.component';

export const routes: Routes = [
  {path: '', redirectTo: '/home', pathMatch: 'full'},
  {path: 'home', component: HomeComponent},
  {path: 'validate', component: ValidateComponent, resolve: {datasets: DatasetResolver}},
  {path: 'validation-result/:validationId', component: ValidationResultComponent},
  {path: 'my-validations', component: ValidationsComponent, canActivate: [AuthGuard], data: {requiresAuth: true}},
  {path: 'user-profile', component: UserProfileComponent, canActivate: [AuthGuard], data: {requiresAuth: true}},
  {path: 'published-validations', component: PublishedValidationsComponent},
  {path: 'help', component: HelpComponent},
  {path: 'terms', component: TermsComponent},
  {path: 'datasets', component: DatasetInfoComponent},
  {path: 'comparison', component: ComparisonComponent, canActivate: [AuthGuard], data: {requiresAuth: true}},
  {path: 'signup', component: SignupComponent, canActivate: [AuthGuard], data: {requiresAuth: false}},
  {path: 'signup-complete', component: SignupCompleteComponent, canActivate: [AuthGuard], data: {requiresAuth: false}},
  {path: 'deactivate-user-complete', component: DeactivateUserCompleteComponent},
  {path: 'password-reset', component: PasswordResetComponent},
  {path: 'password-reset-done', component: PasswordResetDoneComponent},
  {path: 'password-reset/:token', component: PasswordResetValidateTokenComponent},
  {path: 'set-password', component: SetPasswordComponent},
  {path: 'my-datasets', component: MyDatasetsComponent, canActivate: [AuthGuard], data: {requiresAuth: true}},
  {path: 'user-data-guidelines', component: UserDataGuidelinesComponent},
  {path: 'user-data-guidelines2', component: UserDataGuidelinesComponent2},
  {path: 'contact-us', component: ContactUsComponent},
  {path: 'public-api', component: PublicApiComponent},
  {path: 'json-config', component: JsonConfigComponent},
  {path: 'customise-plots', component: CustomisePlotsComponent},
  {path: '**', component: ErrorPageComponent}
];

const routerOptions: ExtraOptions = {
  scrollPositionRestoration: 'enabled',
  anchorScrolling: 'enabled',
  scrollOffset: [0, 100],
};

@NgModule({
  imports: [RouterModule.forRoot(routes, routerOptions)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

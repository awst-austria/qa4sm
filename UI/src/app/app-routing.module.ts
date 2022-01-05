import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {ErrorComponent} from './pages/error/error.component';
import {AuthGuard} from './auth.guard';
import {ValidationResultComponent} from './pages/validation-result/validation-result.component';
import {LoginComponent} from './pages/login/login.component';
import {UserProfileComponent} from './pages/user-profile/user-profile.component';
import {PublishedValidationsComponent} from './pages/published-validations/published-validations.component';
import {ValidationsComponent} from './pages/validations/validations.component';
import {AboutComponent} from './pages/about/about.component';
import {TermsComponent} from './pages/terms/terms.component';
import {DatasetInfoComponent} from './pages/dataset-info/dataset-info.component';
import {HelpComponent} from './pages/help/help.component';
import {SignupComponent} from './pages/signup/signup.component';
import {SignupCompleteComponent} from './pages/signup-complete/signup-complete.component';
import {DeactivateUserCompleteComponent} from './pages/deactivate-user-complete/deactivate-user-complete.component';
import {DatasetResolver} from './modules/core/services/dataset/dataset.resolver';
import {PasswordResetComponent} from './pages/password-reset/password-reset.component';
import {PasswordResetDoneComponent} from './pages/password-reset-done/password-reset-done.component';
import {SetPasswordComponent} from './pages/set-password/set-password.component';
import {
  PasswordResetValidateTokenComponent
} from './pages/password-reset-validate-token/password-reset-validate-token.component';


const routes: Routes = [
  {path: '', redirectTo: '/home', pathMatch: 'full'},
  {path: 'home', component: HomeComponent},
  {path: 'login', component: LoginComponent},
  {path: 'validate', component: ValidateComponent, canActivate: [AuthGuard], resolve: {datasets: DatasetResolver}},
  {path: 'validation-result/:validationId', component: ValidationResultComponent},
  {path: 'my-validations', component: ValidationsComponent, canActivate: [AuthGuard]},
  {path: 'user-profile', component: UserProfileComponent, canActivate: [AuthGuard]},
  {path: 'published-validations', component: PublishedValidationsComponent},
  {path: 'about', component: AboutComponent},
  {path: 'help', component: HelpComponent},
  {path: 'terms', component: TermsComponent},
  {path: 'datasets', component: DatasetInfoComponent},
  {path: 'signup', component: SignupComponent},
  {path: 'signup-complete', component: SignupCompleteComponent},
  {path: 'deactivate-user-complete', component: DeactivateUserCompleteComponent},
  {path: 'password-reset', component: PasswordResetComponent},
  {path: 'password-reset-done', component: PasswordResetDoneComponent},
  {path: 'password-reset/:token', component: PasswordResetValidateTokenComponent},
  {path: 'set-password', component: SetPasswordComponent},
  {path: '**', component: ErrorComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

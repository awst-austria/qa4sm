import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {ErrorComponent} from './pages/error/error.component';
import {AuthGuard} from './auth.guard';
import {ValidationComponent} from './pages/validation/validation.component';
import {LoginComponent} from './pages/login/login.component';
import {UserProfileComponent} from './pages/user-profile/user-profile.component';

const routes: Routes = [
  {path: '', redirectTo: '/home', pathMatch: 'full'},
  {path: 'home', component: HomeComponent},
  {path: 'login', component: LoginComponent},
  {path: 'validate', component: ValidateComponent, canActivate: [AuthGuard]},
  {path: 'validation/:validationId', component: ValidationComponent, canActivate: [AuthGuard]},
  {path: 'validations', component: ValidateComponent, canActivate: [AuthGuard]},
  {path: 'user-profile', component: UserProfileComponent, canActivate: [AuthGuard]},
  {path: '**', component: ErrorComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

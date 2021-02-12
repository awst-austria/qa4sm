import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {ErrorComponent} from './pages/error/error.component';
import {AuthGuard} from './auth.guard';
import {ValidationComponent} from './pages/validation/validation.component';

const routes: Routes = [
  {path: '', redirectTo: '/home', pathMatch: 'full'},
  {path: 'home', component: HomeComponent},
  {path: 'validate', component: ValidateComponent, canActivate: [AuthGuard]},
  {path: 'validation/:validationId', component: ValidationComponent, canActivate: [AuthGuard]},
  {path: 'validations', component: ValidateComponent, canActivate: [AuthGuard]},
  {path: '**', component: ErrorComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

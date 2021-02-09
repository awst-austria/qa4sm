import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';

const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'validate', component: ValidateComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}

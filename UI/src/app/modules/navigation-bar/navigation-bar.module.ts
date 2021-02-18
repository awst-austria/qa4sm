import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavigationBarComponent} from './components/navigation-bar/navigation-bar.component';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';
import {RouterModule} from '@angular/router';



@NgModule({
  declarations: [NavigationBarComponent],
  exports: [
    NavigationBarComponent
  ],
  imports: [
    CommonModule,
    FontAwesomeModule,
    NgbModule,
    RouterModule
  ]
})
export class NavigationBarModule {
}

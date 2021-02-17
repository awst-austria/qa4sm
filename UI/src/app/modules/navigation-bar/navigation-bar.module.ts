import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavigationBarComponent} from './components/navigation-bar/navigation-bar.component';



@NgModule({
  declarations: [NavigationBarComponent],
  exports: [
    NavigationBarComponent
  ],
  imports: [
    CommonModule
  ]
})
export class NavigationBarModule {
}

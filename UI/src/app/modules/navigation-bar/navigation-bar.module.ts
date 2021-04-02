import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavigationBarComponent} from './components/navigation-bar/navigation-bar.component';
import {RouterModule} from '@angular/router';
import {MenubarModule} from 'primeng/menubar';


@NgModule({
  declarations: [NavigationBarComponent],
  exports: [
    NavigationBarComponent
  ],
  imports: [
    CommonModule,
    RouterModule,
    MenubarModule
  ]
})
export class NavigationBarModule {
}

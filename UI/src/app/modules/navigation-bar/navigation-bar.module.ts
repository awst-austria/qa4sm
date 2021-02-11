import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavigationBarComponent} from './components/navigation-bar/navigation-bar.component';
import {MenubarModule} from 'primeng/menubar';


@NgModule({
  declarations: [NavigationBarComponent],
  exports: [
    NavigationBarComponent
  ],
  imports: [
    CommonModule,
    MenubarModule
  ]
})
export class NavigationBarModule {
}

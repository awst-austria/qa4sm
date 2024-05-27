import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {NavigationBarComponent} from './components/navigation-bar-header/navigation-bar.component';
import {RouterModule} from '@angular/router';
import {MenubarModule} from 'primeng/menubar';
import {NavigationFooterComponent} from './components/navigation-footer/navigation-footer.component';
import {ImageModule} from 'primeng/image';


@NgModule({
  declarations: [NavigationBarComponent, NavigationFooterComponent],
  exports: [
    NavigationBarComponent,
    NavigationFooterComponent
  ],
    imports: [
        CommonModule,
        RouterModule,
        MenubarModule,
        ImageModule
    ]
})
export class NavigationBarModule {
}

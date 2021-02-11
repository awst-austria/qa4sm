import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {MenubarModule} from 'primeng/menubar';
import {HomeComponent} from './pages/home/home.component';
import {ValidateComponent} from './pages/validate/validate.component';
import {FormsModule} from '@angular/forms';
import {NavigationBarModule} from './modules/navigation-bar/navigation-bar.module';
import {Carousel, CarouselModule} from 'primeng/carousel';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ValidateComponent
  ],
  imports: [
    NavigationBarModule,
    FormsModule,
    BrowserModule,
    AppRoutingModule,
    MenubarModule,
    CarouselModule

  ],
  providers: [

  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}

import {NgModule} from '@angular/core';
import {ContactFormComponent} from './components/contact-form/contact-form.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [
    ContactFormComponent
  ],
  exports: [
    ContactFormComponent
  ],
    imports: [
        SharedPrimeNgModule,
    ]
})
export class ContactModule { }

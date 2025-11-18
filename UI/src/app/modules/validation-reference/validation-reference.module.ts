import {NgModule} from '@angular/core';
import {ValidationReferenceComponent} from './components/validation-reference/validation-reference.component';
import { SharedPrimeNgModule } from 'src/app/shared.primeNg.module';

@NgModule({
  declarations: [ValidationReferenceComponent],
  exports: [ValidationReferenceComponent],
    imports: [
        SharedPrimeNgModule
    ]
})
export class ValidationReferenceModule { }

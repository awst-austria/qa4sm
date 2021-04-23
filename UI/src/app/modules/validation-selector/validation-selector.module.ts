import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ValidationSelectorComponent} from './components/validation-selector/validation-selector.component';
import {FormsModule} from '@angular/forms';
import {DropdownModule} from 'primeng/dropdown';
import {ButtonModule} from 'primeng/button';

@NgModule({
  declarations: [ValidationSelectorComponent],
  exports: [
    ValidationSelectorComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    DropdownModule,
    ButtonModule
  ]
})
export class ValidationSelectorModule {
}

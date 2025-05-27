import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContactFormComponent } from './components/contact-form/contact-form.component';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { DropdownModule } from 'primeng/dropdown';
import { InputTextModule } from 'primeng/inputtext';
import { PaginatorModule } from 'primeng/paginator';
import { ReactiveFormsModule } from '@angular/forms';
import { TooltipModule } from 'primeng/tooltip';
import { SliderModule } from 'primeng/slider';
import { Textarea } from 'primeng/textarea';


@NgModule({
  declarations: [
    ContactFormComponent
  ],
  exports: [
    ContactFormComponent
  ],
  imports: [
    CommonModule,
    ButtonModule,
    CheckboxModule,
    DropdownModule,
    InputTextModule,
    PaginatorModule,
    ReactiveFormsModule,
    TooltipModule,
    SliderModule,
    Textarea
  ]
})
export class ContactModule { }

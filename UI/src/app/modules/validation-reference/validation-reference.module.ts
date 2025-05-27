import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationReferenceComponent } from './components/validation-reference/validation-reference.component';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule } from '@angular/forms';
import { TooltipModule } from 'primeng/tooltip';


@NgModule({
  exports: [ValidationReferenceComponent],
  imports: [
    CommonModule,
    DropdownModule,
    FormsModule,
    TooltipModule,
    ValidationReferenceComponent
  ]
})
export class ValidationReferenceModule { }

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationReferenceComponent } from './components/validation-reference/validation-reference.component';
import { FormsModule } from '@angular/forms';
import { TooltipModule } from 'primeng/tooltip';
import { Select } from 'primeng/select';


@NgModule({
  declarations: [ValidationReferenceComponent],
  exports: [ValidationReferenceComponent],
  imports: [
    CommonModule,
    FormsModule,
    TooltipModule,
    Select
  ]
})
export class ValidationReferenceModule { }

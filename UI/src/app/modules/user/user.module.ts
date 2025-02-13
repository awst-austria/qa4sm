import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {UserFormComponent} from './user-form/user-form.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {InputTextModule} from 'primeng/inputtext';
import {DropdownModule} from 'primeng/dropdown';
import {TooltipModule} from 'primeng/tooltip';
import {ButtonModule} from 'primeng/button';
import {CheckboxModule} from 'primeng/checkbox';
import {RouterModule} from '@angular/router';
import {SliderModule} from 'primeng/slider';
import {MaintenanceModeComponent} from "../core/maintenance-mode/maintenance-mode.component";


@NgModule({
  declarations: [UserFormComponent],
  exports: [
    UserFormComponent
  ],
    imports: [
        CommonModule,
        ReactiveFormsModule,
        InputTextModule,
        DropdownModule,
        FormsModule,
        TooltipModule,
        ButtonModule,
        CheckboxModule,
        RouterModule,
        SliderModule,
        MaintenanceModeComponent,
    ]
})
export class UserModule { }

// src/app/shared/shared.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ConfirmationService, MessageService } from 'primeng/api';

// PrimeNG (v20) 
import { AccordionContent, AccordionHeader, AccordionModule, AccordionPanel } from 'primeng/accordion';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { CarouselModule } from 'primeng/carousel';
import { CheckboxModule } from 'primeng/checkbox';
import { ChipModule } from 'primeng/chip';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
   
import { DialogModule } from 'primeng/dialog';
import { FieldsetModule } from 'primeng/fieldset';
import { GalleriaModule } from 'primeng/galleria';
import { ImageModule } from 'primeng/image';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { MenuModule } from 'primeng/menu';
import { MultiSelectModule } from 'primeng/multiselect';
import { PanelModule } from 'primeng/panel';
import { PasswordModule } from 'primeng/password';
import { ProgressBarModule } from 'primeng/progressbar';
import { RippleModule } from 'primeng/ripple';
import { ScrollTopModule } from 'primeng/scrolltop';
import { SelectButtonModule } from 'primeng/selectbutton';

import { ToastModule } from 'primeng/toast';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { TooltipModule } from 'primeng/tooltip';
import { SliderModule } from 'primeng/slider';
import { DatePickerModule } from 'primeng/datepicker';
import { PaginatorModule } from 'primeng/paginator';
import { MenubarModule } from 'primeng/menubar';
import { DividerModule } from 'primeng/divider';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { PanelMenuModule } from 'primeng/panelmenu';
import { SelectModule } from 'primeng/select';

@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,

    // PrimeNG 
    AccordionModule,
    AccordionPanel,
    AccordionHeader,
    AccordionContent,
    ButtonModule,
    CardModule,
    CarouselModule,
    CheckboxModule,
    ChipModule,
    ConfirmDialogModule,
    DatePickerModule,
    DialogModule,
    DividerModule,
    FontAwesomeModule,
    FieldsetModule,
    GalleriaModule,
    ImageModule,
    InputNumberModule,
    InputTextModule,
    MenubarModule,
    MenuModule,
    MultiSelectModule,
    PaginatorModule,
    PanelMenuModule,
    PanelModule,
    PasswordModule,
    ProgressBarModule,
    RippleModule,
    ScrollPanelModule,
    ScrollTopModule,
    SelectButtonModule,
    SelectModule,
    SliderModule,
    ToastModule,
    ToggleButtonModule,
    TooltipModule,
  ],
  exports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,

    // PrimeNG 
    AccordionModule,
    AccordionPanel,
    AccordionHeader,
    AccordionContent,
    ButtonModule,
    CardModule,
    CarouselModule,
    CheckboxModule,
    ChipModule,
    ConfirmDialogModule,
    DatePickerModule,
    DialogModule,
    DividerModule,
    FieldsetModule,
    FontAwesomeModule,
    GalleriaModule,
    ImageModule,
    InputNumberModule,
    InputTextModule,
    MenubarModule,
    MenuModule,
    MultiSelectModule,
    PaginatorModule,
    PanelMenuModule,
    PanelModule,
    PasswordModule,
    ProgressBarModule,
    RippleModule,
    ScrollPanelModule,
    ScrollTopModule,
    SelectButtonModule,
    SelectModule,
    SliderModule,
    ToastModule,
    ToggleButtonModule,
    TooltipModule,
  ],
  providers: [
    ConfirmationService,      
    MessageService            
  ]
})
export class SharedPrimeNgModule {}

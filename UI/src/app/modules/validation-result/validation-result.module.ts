import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationrunRowComponent } from './components/validationrun-row/validationrun-row.component';



@NgModule({
    declarations: [ValidationrunRowComponent],
    exports: [
        ValidationrunRowComponent
    ],
    imports: [
        CommonModule
    ]
})
export class ValidationResultModule { }

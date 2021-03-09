import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ValidationrunRowComponent} from './components/validationrun-row/validationrun-row.component';
import {PanelModule} from 'primeng/panel';
import {TooltipModule} from 'primeng/tooltip';


@NgModule({
    declarations: [ValidationrunRowComponent],
    exports: [
        ValidationrunRowComponent
    ],
    imports: [
        CommonModule,
        PanelModule,
        TooltipModule
    ]
})
export class ValidationResultModule { }

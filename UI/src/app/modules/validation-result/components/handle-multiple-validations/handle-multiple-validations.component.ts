import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {MenuItem} from 'primeng/api';

@Component({
    selector: 'qa-handle-multiple-validations',
    templateUrl: './handle-multiple-validations.component.html',
    styleUrls: ['./handle-multiple-validations.component.scss']
})
export class HandleMultipleValidationsComponent implements OnInit {
    @Output() selectionActive = new EventEmitter();

    items: MenuItem[];

    ngOnInit() {
        this.items = [
            {
                label: 'Delete',
                icon: 'pi pi-fw pi-trash',
                items: [
                    {
                        label: 'Select one by one',
                        items: [
                            {
                                label: 'Select all',
                                icon: 'pi pi-fw pi-check-square'
                            },
                            {
                                label: 'Select individually',
                                icon: 'pi pi-fw pi-square'
                            }
                        ]
                    },
                    {
                        label: 'Select a group',
                        icon: 'pi pi-fw pi-calendar'
                    },
                ]
            }
        ]
    }

    activateSelection(): void{
        this.selectionActive.emit(true)
    }

}

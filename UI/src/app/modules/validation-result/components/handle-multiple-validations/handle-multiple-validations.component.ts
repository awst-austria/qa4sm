import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {MenuItem} from 'primeng/api';

@Component({
    selector: 'qa-handle-multiple-validations',
    templateUrl: './handle-multiple-validations.component.html',
    styleUrls: ['./handle-multiple-validations.component.scss']
})
export class HandleMultipleValidationsComponent implements OnInit {
    @Output() selectionActive = new EventEmitter();

    deleteItems: MenuItem[];

    ngOnInit() {
        this.deleteItems = [
            {
                label: 'Delete',
                icon: 'pi pi-fw pi-trash',
                items: [
                    {
                        label: 'Select one by one',
                        items: [
                            {
                                label: 'Select all',
                                icon: 'pi pi-fw pi-check-square',
                                command: () => this.activateSelection(true)
                            },
                            {
                                label: 'Select individually',
                                icon: 'pi pi-fw pi-stop',
                                command: () => this.activateSelection(false)
                            }
                        ]
                    },
                    {
                        label: 'Select a group',
                        items: [
                            {
                                label: 'Select by date',
                                icon: 'pi pi-fw pi-calendar'
                            },
                            {
                                label: 'Select by data set',
                                icon: 'pi pi-fw pi-file'
                            }
                        ]
                    },
                ]
            }
        ]
    }

    activateSelection(allSelected): void{
        this.selectionActive.emit({activate: true, selectAll: allSelected})
    }

}

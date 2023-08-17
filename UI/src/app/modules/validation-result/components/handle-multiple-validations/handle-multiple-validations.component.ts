import {Component, OnInit} from '@angular/core';
import {MenuItem} from 'primeng/api';

@Component({
  selector: 'qa-handle-multiple-validations',
  templateUrl: './handle-multiple-validations.component.html',
  styleUrls: ['./handle-multiple-validations.component.scss']
})
export class HandleMultipleValidationsComponent implements OnInit  {
  items: MenuItem[];

  ngOnInit() {
    this.items = [
      {label: 'Delete',
      icon: 'pi pi-fw pi-trash'}
    ]
  }

}

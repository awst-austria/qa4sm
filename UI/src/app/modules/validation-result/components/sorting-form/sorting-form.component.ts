import {Component, EventEmitter, Output} from '@angular/core';
import {SortChoicesModel} from './sort-choices-model';
import {SortOrderModel} from './sort-order-model';


export const ORDER_DIRECTION_DESC = 'descending';
export const ORDER_DIRECTION_DESC_PREP = '-';

export const ORDER_DIRECTION_ASC = 'ascending';
export const ORDER_DIRECTION_ASC_PREP = '';


@Component({
  selector: 'qa-sorting-form',
  templateUrl: './sorting-form.component.html',
  styleUrls: ['./sorting-form.component.scss']
})
export class SortingFormComponent {
  @Output() orderQueryName = new EventEmitter<string>();

  public sortingChoices: SortChoicesModel[] = [
    {
      displayName: 'Date',
      queryName: 'start_time:asc'
    },
    {
      displayName: 'Name',
      queryName: 'name'
    },
    {
      displayName: "Status",
      queryName: 'progress'
    },
    {
      displayName: 'Spatial reference dataset',
      queryName: 'spatial_reference_dataset'
    }
  ];

  public orderChoices: SortOrderModel[] = [
    {
      direction: 'descending',
      querySuffix: 'desc'
    },
    {
      direction: 'ascending',
      querySuffix: 'asc'
    }

  ];

  selectedChoicesModel: SortChoicesModel = this.sortingChoices[0];
  selectedOrderModel: SortOrderModel = this.orderChoices[0];

  constructor() {
  }

  onSortingChange(): void {
    const order = `${this.selectedChoicesModel.queryName}:${this.selectedOrderModel.querySuffix}`;
    this.orderQueryName.emit(order);
  }

}

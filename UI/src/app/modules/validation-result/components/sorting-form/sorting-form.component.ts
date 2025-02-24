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
      queryName: 'start_time'
    },
    {
      displayName: 'Name',
      queryName: 'name_tag'
    },
    {
      displayName: "Status",
      queryName: 'progress'
    },
    {
      displayName: 'Spatial reference dataset',
      queryName: 'spatial_reference_configuration_id__dataset__pretty_name'
    }
  ];

  public orderChoices: SortOrderModel[] = [
    {
      direction: 'descending',
      queryPrefix: '-'
    },
    {
      direction: 'ascending',
      queryPrefix: ''
    }

  ];

  selectedChoicesModel: SortChoicesModel = this.sortingChoices[0];
  selectedOrderModel: SortOrderModel = this.orderChoices[0];

  constructor() {
  }

  onSortingChange(): void {
    const order = this.selectedOrderModel.queryPrefix + this.selectedChoicesModel.queryName;
    this.orderQueryName.emit(order);
  }

}

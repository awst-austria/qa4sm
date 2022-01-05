import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {SortChoicesModel} from './sort-choices-model';
import {SortOrderModel} from './sort-order-model';


export const SORT_BY_TIME_DISPLAY_NAME = 'Date';
export const SORT_BY_TIME_QUERY_NAME = 'start_time';

export const SORT_BY_NAME_DISPLAY_NAME = 'Name';
export const SORT_BY_NAME_QUERY_NAME = 'name_tag';

export const SORT_BY_STATUS_DISPLAY_NAME = 'Status';
export const SORT_BY_STATUS_QUERY_NAME = 'progress';

export const SORT_BY_REFERENCE_DISPLAY_NAME = 'Reference dataset';
export const SORT_BY_REFERENCE_QUERY_NAME = 'reference_configuration_id__dataset__pretty_name';

export const ORDER_DIRECTION_DESC = 'descending';
export const ORDER_DIRECTION_DESC_PREP = '-';

export const ORDER_DIRECTION_ASC = 'ascending';
export const ORDER_DIRECTION_ASC_PREP = '';


@Component({
  selector: 'qa-sorting-form',
  templateUrl: './sorting-form.component.html',
  styleUrls: ['./sorting-form.component.scss']
})
export class SortingFormComponent implements OnInit {
  sortingChoicesModels: SortChoicesModel[] = [];
  selectedChoicesModel: SortChoicesModel;
  orderChoicesModels: SortOrderModel[] = [];
  selectedOrderModel: SortOrderModel;
  @Output() orderQueryName =  new EventEmitter<string>();

  constructor() { }

  ngOnInit(): void {
    this.prepareSortingChoices();
    this.prepareSortingOrder();
  }

  onSortingChange(): void{
    const order = this.selectedOrderModel.queryPrependix + this.selectedChoicesModel.queryName;
    this.orderQueryName.emit(order);
  }

  private prepareSortingChoices(): void{
    this.sortingChoicesModels.push(new SortChoicesModel(SORT_BY_TIME_DISPLAY_NAME, SORT_BY_TIME_QUERY_NAME));
    this.sortingChoicesModels.push(new SortChoicesModel(SORT_BY_NAME_DISPLAY_NAME, SORT_BY_NAME_QUERY_NAME));
    this.sortingChoicesModels.push(new SortChoicesModel(SORT_BY_STATUS_DISPLAY_NAME, SORT_BY_STATUS_QUERY_NAME));
    this.sortingChoicesModels.push(new SortChoicesModel(SORT_BY_REFERENCE_DISPLAY_NAME, SORT_BY_REFERENCE_QUERY_NAME));
    this.selectedChoicesModel = this.sortingChoicesModels[0];
  }

  private prepareSortingOrder(): void{
    this.orderChoicesModels.push(new SortOrderModel(ORDER_DIRECTION_DESC, ORDER_DIRECTION_DESC_PREP));
    this.orderChoicesModels.push(new SortOrderModel(ORDER_DIRECTION_ASC, ORDER_DIRECTION_ASC_PREP));
    this.selectedOrderModel = this.orderChoicesModels[0];
  }

}

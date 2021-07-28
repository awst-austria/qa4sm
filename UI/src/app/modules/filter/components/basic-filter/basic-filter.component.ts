import {Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import {FilterModel} from './filter-model';

@Component({
  selector: 'qa-basic-filter',
  templateUrl: './basic-filter.component.html',
  styleUrls: ['./basic-filter.component.scss']
})
export class BasicFilterComponent implements OnInit {

  @Input() filterModel: FilterModel;
  @Output() onExcludeMutual = new EventEmitter<number>();

  constructor() {
  }

  ngOnInit(): void {
  }

  exclude_filters(event: Event): void {
    // should tell the parent to uncheck the mutually exclusive filter(s), if any
    const toDisable = this.filterModel.filterDto.disable_filter;
    if (toDisable !== null && this.filterModel.enabled) {
      this.onExcludeMutual.emit(toDisable)
    }
  }
}

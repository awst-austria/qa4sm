import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FilterModel} from './filter-model';

@Component({
  selector: 'qa-basic-filter',
  templateUrl: './basic-filter.component.html',
  styleUrls: ['./basic-filter.component.scss']
})
export class BasicFilterComponent implements OnInit {

  @Input() filterModel: FilterModel;
  @Input() isIncluded: boolean;
  @Output() onIncludeMutual = new EventEmitter<string>();
  @Output() onMutuallyIncluded = new EventEmitter<string>();
  @Output() onExcludeMutual = new EventEmitter<number>();

  constructor() {
  }

  ngOnInit(): void {
    console.log(this.filterModel.filterDto.description, this.filterModel.filterDto.to_include);
  }

  include_filters(event: Event): void {
    // Tell the parent to check the other inclusive filters, if any
    const to_include = this.filterModel.filterDto.to_include;
    if (to_include !== null) {
      this.onIncludeMutual.emit(to_include);
    }
  }

  exclude_filters(event: Event): void {
    // should tell the parent to uncheck the mutually exclusive filter(s), if any
    const toDisable = this.filterModel.filterDto.disable_filter;
    if (toDisable !== null && this.filterModel.enabled) {
      this.onExcludeMutual.emit(toDisable);
    }
  }
}

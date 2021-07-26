import {Component, Input, OnInit, Output, EventEmitter} from '@angular/core';
import {FilterModel} from './filter-model';

@Component({
  selector: 'qa-basic-filter',
  templateUrl: './basic-filter.component.html',
  styleUrls: ['./basic-filter.component.scss']
})
export class BasicFilterComponent implements OnInit {

  @Input() filterModel: FilterModel;
  @Output() onIncludeMutual = new EventEmitter<string>();
  @Output() onMutuallyIncluded = new EventEmitter<string>();

  constructor() {
  }

  ngOnInit(): void {
  }

  include_filters(event: Event): void {
    // Tell the parent to check the other inclusive filters, if any
    const to_include = this.filterModel.filterDto.to_include;
    if (to_include !== null) {
      this.onIncludeMutual.emit(to_include)
    }
  }
}

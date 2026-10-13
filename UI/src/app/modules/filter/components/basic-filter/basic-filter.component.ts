import {Component, EventEmitter, Input, Output} from '@angular/core';
import {FilterModel} from './filter-model';

@Component({
    selector: 'qa-basic-filter',
    templateUrl: './basic-filter.component.html',
    styleUrls: ['./basic-filter.component.scss'],
    standalone: false
})
export class BasicFilterComponent  {

  @Input() filterModel: FilterModel;
  @Input() isIncluded: boolean;
  // set while another setting rules this filter out; it is shown as a warning
  // and keeps the filter from being switched on, though never from being
  // switched off
  @Input() blockedReason: string | null = null;
  @Output() includeMutual = new EventEmitter<string>();
  @Output() mutuallyIncluded = new EventEmitter<string>();
  @Output() excludeMutual = new EventEmitter<string>();
  @Output() updateMap = new EventEmitter<boolean>();

  filtersThatUpdateMap = ['FIL_ISMN_FRM_representative'] // todo: get the list from the backend

  constructor() {
  }

  includeFilters(event): void {
    // Tell the parent to check the other inclusive filters, if any
    const to_include = this.filterModel.filterDto.to_include;
    if (to_include !== null) {
      this.includeMutual.emit(to_include);
    }
  }

  excludeFilters(event): void {
    // should tell the parent to uncheck the mutually exclusive filter(s), if any
    const to_exclude = this.filterModel.filterDto.to_exclude;
    if (to_exclude !== null && this.filterModel.enabled) {
      this.excludeMutual.emit(to_exclude);
    }
  }

  isBlocked(): boolean {
    return !!this.blockedReason && !this.filterModel.enabled;
  }

  checkIfUpdateMap(filter): void{
    this.updateMap.emit(this.filtersThatUpdateMap.includes(filter));
  }

}

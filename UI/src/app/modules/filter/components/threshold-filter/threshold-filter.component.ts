import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ThresholdFilterModel} from "./threshold-filter-model";

@Component({
  selector: 'qa-threshold-filter',
  templateUrl: './threshold-filter.component.html',
  styleUrls: ['./threshold-filter.component.scss']
})
export class ThresholdFilterComponent implements OnInit {

  @Input() filterModel: ThresholdFilterModel;

  constructor() { }

  ngOnInit(): void {
  }

  SetParamDefault(): void{
    this.filterModel.selectedValue$.next(this.filterModel.filterDto.default_threshold);
  }

  checkValIfLimited(value: number): any {
    if (
      this.filterModel.selectedValue$.getValue() <= this.filterModel.filterDto.max_threshold &&
      this.filterModel.selectedValue$.getValue() >= this.filterModel.filterDto.min_threshold) {
      return value;
    }
  }

}

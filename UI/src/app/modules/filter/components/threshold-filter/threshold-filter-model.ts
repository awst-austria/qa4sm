import {FilterDto} from "../../../core/services/filter/filter.dto";
import {BehaviorSubject} from "rxjs";

export class ThresholdFilterModel {
  constructor(public filterDto: FilterDto,
              public selectedValue$: BehaviorSubject<number>,) {
  }

}

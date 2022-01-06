import {FilterDto} from '../../../core/services/filter/filter.dto';
import {BehaviorSubject} from 'rxjs';

export class FilterModel {
  constructor(public filterDto: FilterDto,
              public enabled$: BehaviorSubject<boolean>,
              public readonly$: BehaviorSubject<boolean>,
              public parameters$: BehaviorSubject<string>) {
  }
}

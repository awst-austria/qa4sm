import {FilterDto} from '../../../core/services/filter/filter.dto';

export class FilterModel {
  constructor(public filterDto: FilterDto, public enabled: Boolean, public readonly: Boolean, public parameters: string) {
  }
}

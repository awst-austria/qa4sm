import {FilterDto} from '../../services/filter.dto';

export class FilterModel {
  constructor(public filterDto: FilterDto, public enabled: Boolean, public parameters: string) {
  }
}

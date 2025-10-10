import {Component, Input} from '@angular/core';
import {TemporalMatchingModel} from './temporal-matching-model';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';

@Component({
    selector: 'qa-temporal-matching',
    templateUrl: './temporal-matching.component.html',
    styleUrls: ['./temporal-matching.component.scss'],
    standalone: false
})
export class TemporalMatchingComponent  {

  @Input() temporalMatchingModel: TemporalMatchingModel;

  constructor(public globalService: GlobalParamsService) {
  }

  getDefaultSize(): number{
    this.temporalMatchingModel.size$.next(this.globalService.globalContext.temporal_matching_default);
    return this.globalService.globalContext.temporal_matching_default;
  }

}

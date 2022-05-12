import {Component, Input, OnInit} from '@angular/core';
import {TemporalMatchingModel} from './temporal-matching-model';
import {GlobalParamsService} from '../../../core/services/global/global-params.service';

@Component({
  selector: 'qa-temporal-matching',
  templateUrl: './temporal-matching.component.html',
  styleUrls: ['./temporal-matching.component.scss']
})
export class TemporalMatchingComponent implements OnInit {

  @Input() temporalMatchingModel: TemporalMatchingModel;

  constructor(public globalService: GlobalParamsService) {
  }

  ngOnInit(): void {
  }

}

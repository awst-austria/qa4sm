import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../services/validationrun.service';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../services/validationrun.dto';
import {ConfigurationCacheItem, DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {DatasetConfigurationDto} from '../../services/dataset-configuration.dto';
import {GlobalParamsService} from '../../../core/services/gloabal-params/global-params.service';

@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit {
  // with this one I can do *ngFor ... of ...
  publishedValidationruns?: ValidationrunDto[];
  // this one I can use e.g. as [options] in p-dropdown element
  publishedValidation$: Observable<ValidationrunDto[]>;
  // configs$: Observable<ConfigurationDto>;

  constructor() { }

  ngOnInit(): void {
  }

}

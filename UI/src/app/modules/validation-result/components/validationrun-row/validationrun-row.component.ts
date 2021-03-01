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

  @Input() published: boolean = false;
  @Input() valrun: ValidationrunDto;

  constructor(private validationrunService: ValidationrunService, private configurationService: DatasetConfigurationService,
              private globalContextService: GlobalParamsService) { }

  ngOnInit(): void {

  }

  getDoiPrefix(): string {
    return this.globalContextService.globalContext.doi_prefix;
  }

  // getConfigurationOfValidation()

}

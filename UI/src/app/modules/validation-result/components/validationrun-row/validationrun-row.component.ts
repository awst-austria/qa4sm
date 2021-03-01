import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../services/validationrun.service';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../services/validationrun.dto';
import {ConfigurationCacheItem, DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {DatasetConfigurationDto} from '../../services/dataset-configuration.dto';
import {GlobalParamsService} from '../../../core/services/gloabal-params/global-params.service';
import {ValidationConfigurationModel} from '../../services/validation-configuration-model';


@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit {
  datasetsConfigurations: ValidationConfigurationModel[] = [];
  referenceConfiguration: ValidationConfigurationModel[] = []; // this array will always contain exactly 1 element

  @Input() published: boolean = false;
  @Input() valrun: ValidationrunDto;

  constructor(private validationrunService: ValidationrunService, private configurationService: DatasetConfigurationService,
              private globalParamsService: GlobalParamsService) { }

  ngOnInit(): void {
    this.addDatasetToList();
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  addDatasetToList() {
    this.getConfigurationOfPublishedValidation(this.datasetsConfigurations);
  }

  private getConfigurationOfPublishedValidation(targetArray: ValidationConfigurationModel[]){
    let model = new ValidationConfigurationModel('', [], [], null, null, null, null);
    targetArray.push(model);
  //
    this.validationrunService.getPublishedValidationruns().subscribe(publishedVal => {
      model.validationrunId = publishedVal[0].id;
      let validationRefId = publishedVal[0].reference_configuration;

      // this.configurationService.

      // this.configurationService.getConfigByValidationrun(model.validationrunId).subscribe(config => {
      //   model.datasetsVersions = [config[0].version];
      // });

    });
  //
  }

  private updateValidationConfiguration(model: ValidationConfigurationModel){
    this.configurationService.getConfigByValidationrun(model.validationrunId).subscribe(configs => {
      model.datasets = [];
      model.datasetsVersions = [];
      model.datasetsVariables = [];
      configs.forEach(config => {
        model.datasets.push(config.dataset);
        model.datasetsVersions.push(config.version);
        model.datasetsVariables.push(config.variable);
      });
    });
  }

}

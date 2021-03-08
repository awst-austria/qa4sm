import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../services/validationrun.service';
import {ValidationrunDto} from '../../services/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/gloabal-params/global-params.service';
import {ValidationConfigurationModel} from './validation-configuration-model';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';
import {DatasetRowModel} from './dataset-row.model';


@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit {

  validationDatasetsConfigurations: ValidationConfigurationModel[] = [];
  validationReferenceConfiguration: ValidationConfigurationModel[] = []; // this array will always contain exactly 1 element
  datasets?: any;

  @Input() published: boolean = false;
  @Input() valrun: ValidationrunDto;
  @Input() allDatasets: DatasetDto[];
  @Input() allVersions: DatasetVersionDto[];
  @Input() allVariables: DatasetVariableDto[];
  // @Input()  allVersions: DatasetVersionDto[] = [];

  constructor(private validationrunService: ValidationrunService,
              private configurationService: DatasetConfigurationService,
              private globalParamsService: GlobalParamsService) {
  }

  ngOnInit(): void {
    this.addDatasetToList();
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  addDatasetToList() {
    this.getValidationConfiguration(this.validationDatasetsConfigurations, this.validationReferenceConfiguration);
  }

  private getValidationConfiguration(targetDatasetArray: ValidationConfigurationModel[],
                                     targetReferenceArray: ValidationConfigurationModel[]) {

    this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
      configs.forEach(config => {
        let datasetModel = new DatasetRowModel(null, null, null );
        let model = new ValidationConfigurationModel(datasetModel, false);
        model.isReference = config.id === this.valrun.reference_configuration;
        model.datasetConfig.selectedDataset = this.allDatasets.find(value => value.id === config.dataset);
        model.datasetConfig.selectedVersion = this.allVersions.find(value => value.id === config.version);
        model.datasetConfig.selectedVariable = this.allVariables.find(value => value.id === config.variable);
        if (!model.isReference){
          targetDatasetArray.push(model);
        } else {
          targetReferenceArray.push(model);
        }

      });
    });
  }
}

import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../services/validationrun.service';
import {ValidationrunDto} from '../../services/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/gloabal-params/global-params.service';
import {ValidationConfigurationModel} from '../../services/validation-configuration-model';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';
import {DatasetDto} from '../../../dataset/services/dataset.dto';
import {DatasetVersionDto} from '../../../dataset/services/dataset-version.dto';
import {DatasetVariableDto} from '../../../dataset/services/dataset-variable.dto';


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
    this.getValidationConfiguration(this.validationDatasetsConfigurations,this.validationReferenceConfiguration);
  }

  private getValidationConfiguration(targetDatasetArray: ValidationConfigurationModel[],
                                     targetReferenceArray: ValidationConfigurationModel[]) {

    this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
      configs.forEach(config => {
        let datasetModel = new DatasetComponentSelectionModel(null, null, null );
        let datasetConfigModel = new DatasetConfigModel(datasetModel, [], []);
        let model = new ValidationConfigurationModel(datasetConfigModel, false);
        model.isReference = config.id === this.valrun.reference_configuration;
        model.datasetConfig.datasetModel.selectedDataset = this.allDatasets.find(value => value.id === config.dataset);
        model.datasetConfig.datasetModel.selectedVersion = this.allVersions.find(value => value.id === config.version);
        model.datasetConfig.datasetModel.selectedVariable = this.allVariables.find(value => value.id === config.variable);
        if (!model.isReference){
          targetDatasetArray.push(model);
        } else {
          targetReferenceArray.push(model);
        }

      });
    });
  }

//   private getValidationConfiguration(model: ValidationConfigurationModel){
//     this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
//       configs.forEach(config => {
//         model.isReference.push(config.id === this.valrun.reference_configuration);
//         let itemDatasetConfig = new DatasetConfigModel(
//                                 new DatasetComponentSelectionModel(
//                                   null, null, null),
//                                   [], []);
//
//         itemDatasetConfig.datasetModel.selectedDataset = this.allDatasets.find(value => value.id === config.dataset);
//         itemDatasetConfig.datasetModel.selectedVersion = this.allVersions.find(value => value.id === config.version);
//         itemDatasetConfig.datasetModel.selectedVariable = this.allVariables.find(value => value.id === config.variable);
//         // this.datasetVersionService.getVersionById(versionId).subscribe(version => {
//         //   itemDatasetConfig.datasetModel.selectedVersion = version;
//         // });
//         model.datasetConfig.push(itemDatasetConfig);
//       });
//     });
//   }
}

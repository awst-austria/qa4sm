import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../services/validationrun.service';
import {ValidationrunDto} from '../../services/validationrun.dto';
import {DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {GlobalParamsService} from '../../../core/services/gloabal-params/global-params.service';
import {ValidationConfigurationModel} from '../../services/validation-configuration-model';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';
import {DatasetService} from '../../../dataset/services/dataset.service';
import {DatasetVersionService} from '../../../dataset/services/dataset-version.service';


@Component({
  selector: 'qa-validationrun-row',
  templateUrl: './validationrun-row.component.html',
  styleUrls: ['./validationrun-row.component.scss']
})
export class ValidationrunRowComponent implements OnInit {

  // validationDatasetsConfigurations: ValidationConfigurationModel[] = [];
  validationDatasetsConfigurations: ValidationConfigurationModel = {datasetConfig: [], isReference: []};
  validationReferenceConfiguration: ValidationConfigurationModel[] = []; // this array will always contain exactly 1 element

  @Input() published: boolean = false;
  @Input() valrun: ValidationrunDto;

  constructor(private validationrunService: ValidationrunService,
              private configurationService: DatasetConfigurationService,
              private globalParamsService: GlobalParamsService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService) {
    // const validationDatasetsConfigurations = new ValidationConfigurationModel(this.valrun.id, [], [], null, null, null, null);

  }

  ngOnInit(): void {
    this.addDatasetToList();
    console.log(this.validationDatasetsConfigurations);
  }

  getDoiPrefix(): string {
    return this.globalParamsService.globalContext.doi_prefix;
  }

  addDatasetToList() {
    this.getValidationConfiguration(this.validationDatasetsConfigurations);
  }

  // private getValidationConfiguration(targetArray: ValidationConfigurationModel[]) {
  //   this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
  //     configs.forEach(config => {
  //       let datasetModel = new DatasetComponentSelectionModel(null, null, null );
  //       let model = new ValidationConfigurationModel(new DatasetConfigModel(datasetModel, [], []), false);
  //       targetArray.push(model);
  //       model.isReference = config.id === this.valrun.reference_configuration;
  //       let datasetId = config.dataset;
  //       let versionId = config.version;
  //       let variableId = config.variable;
  //       // console.log(config);
  //       this.datasetService.getDatasetById(datasetId).subscribe(dataset => {
  //         // console.log(dataset);
  //         model.datasetConfig.datasetModel.selectedDataset = dataset;
  //       });
  //       this.datasetVersionService.getVersionById(versionId).subscribe(version => {
  //               model.datasetConfig.datasetModel.selectedVersion = version;
  //             });
  //     });
  //   });
  // }

  private getValidationConfiguration(model: ValidationConfigurationModel){
    this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
      configs.forEach(config => {
        model.isReference.push(config.id === this.valrun.reference_configuration);
        let itemDatasetConfig = new DatasetConfigModel(
                                new DatasetComponentSelectionModel(
                                  null, null, null),
                                  [], []);
        let datasetId = config.dataset;
        let versionId = config.version;
        let variableId = config.variable;
        this.datasetService.getDatasetById(datasetId).subscribe(dataset => {
          itemDatasetConfig.datasetModel.selectedDataset = dataset;
        });
        this.datasetVersionService.getVersionById(versionId).subscribe(version => {
          itemDatasetConfig.datasetModel.selectedVersion = version;
        });
        model.datasetConfig.push(itemDatasetConfig);
      });
    });
  }
}

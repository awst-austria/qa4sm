import {Component, Input, OnInit} from '@angular/core';
import {ValidationrunService} from '../../services/validationrun.service';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../services/validationrun.dto';
import {ConfigurationCacheItem, DatasetConfigurationService} from '../../services/dataset-configuration.service';
import {DatasetConfigurationDto} from '../../services/dataset-configuration.dto';
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

  private getValidationConfiguration(model: ValidationConfigurationModel){
    this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
      configs.forEach(config => {
        model.isReference.push(config.id === this.valrun.reference_configuration);
        let itemDatasetConfig = new DatasetConfigModel(
                                new DatasetComponentSelectionModel(
                                  null, null, null),
                                  [], []);
        let versionId = config.version;
        let variableId = config.variable;
        this.datasetService.getDatasetById(config.dataset).subscribe(dataset => {
          itemDatasetConfig.datasetModel.selectedDataset = dataset;
        });
        // this.datasetService.getAllDatasets().subscribe(datasets => {
        //   itemDatasetConfig.datasetModel.selectedDataset = datasets[0];
        //   console.log(datasets[0]);
        // });
        model.datasetConfig.push(itemDatasetConfig);
      });
    });


    // this.updateValidationConfiguration(model);
  }


  //
  // addDatasetToList() {
  //   this.getValidationConfiguration(this.validationDatasetsConfigurations);
  // }
  //
  // private getValidationConfiguration(targetArray: ValidationConfigurationModel[]){
  //   let model = new ValidationConfigurationModel(
  //     new DatasetConfigModel(
  //       new DatasetComponentSelectionModel(null, null, null),
  //       null, null), false);
  //   console.log(targetArray);
  //   // model.datasetConfig.datasetModel.selectedDataset
  //   this.configurationService.getConfigByValidationrun(this.valrun.id).subscribe(configs => {
  //     configs.forEach(config => {
  //       model.isReference = config.id === this.valrun.reference_configuration;
  //       console.log(config.dataset, config.version, config.variable, config.id === this.valrun.reference_configuration);
  //     });
  //   });
  //   targetArray.push(model);


  // private getConfigurationOfPublishedValidation(model: ValidationConfigurationModel[]){
  //   // let model = new ValidationConfigurationModel(this.valrun.id, [], [], null, null, null, null);
  // // //
  // //   this.validationrunService.getPublishedValidationruns().subscribe(publishedVal => {
  // //     model.validationrunId = publishedVal[0].id;
  // //     let validationRefId = publishedVal[0].reference_configuration;
  // //
  // //     this.configurationService.getConfigById(validationRefId).subscribe(refConfig => {
  // //       model.refDataset = refConfig.dataset;
  // //       model.refDatasetVariable = refConfig.variable;
  // //       model.refDatasetVersion = refConfig.version;
  // //     });
  // //
  //   this.updateValidationConfiguration(model);
  // //
  // //   });
  // //
  // }

  private updateValidationConfiguration(model: ValidationConfigurationModel){
    console.log('Monika');
  }
//   private updateValidationConfiguration(model: ValidationConfigurationModel){
//     this.configurationService.getConfigByValidationrun(model.validationrunId).subscribe(configs => {
//       model.datasets = [];
//       model.datasetVersion = [];
//       model.datasetsVariables = [];
//       configs.forEach(config => {
//         model.datasets.push(config.dataset);
//         model.datasetsVersions.push(config.version);
//         model.datasetsVariables.push(config.variable);
//       });
//     });
//   }
//



}

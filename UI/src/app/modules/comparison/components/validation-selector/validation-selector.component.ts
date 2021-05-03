import {Component, OnInit} from '@angular/core';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';
import {Validations2CompareModel} from './validation-selection.model';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ExtentModel} from '../spatial-extent/extent-model';

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  maxDatasets: number = 3;
  // how to provide a number parameter to HttpParams?
  // Monika: the same as all the parameters, just convert it to string and then to int on the backend side
  selectedDatasetModel: DatasetConfigModel[] = [];
  // new DatasetConfigModel(null, null, null);
  comparisonModel: Validations2CompareModel = new Validations2CompareModel([]);
  spatialExtent: ExtentModel;
  validations4Comparison: ValidationrunDto[] = [];
  selectedValidation: ValidationrunDto;

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    // you have already created this object in line 17, there is no need to do it one more time
    // this.comparisonModel = new Validations2CompareModel();
    this.addDatasetToSelection();
    this.generateExtentOptions();
  }

  addDatasetToSelection(): void {
    this.selectDataset(this.selectedDatasetModel);
  }

  private selectDataset(selected: DatasetConfigModel[]): void {
    const model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
    selected.push(model);
    //get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      model.datasetModel.selectedDataset = datasets[0];

      //then get all versions for the first dataset in the result list
      this.versionService.getVersionsByDataset(model.datasetModel.selectedDataset.id).subscribe(versions => {
        model.datasetModel.selectedVersion = versions[0];

        const parameters = new HttpParams()
          .set('ref_dataset', String(datasets[0].short_name))
          .set('ref_version', String(versions[0].short_name));
        console.log(parameters);

        this.validationrunService.getValidationsForComparison(parameters).subscribe(response => {
          // const validations = response;
          // console.log(validations);
          console.log(response);
          this.validations4Comparison = response;
          this.selectedValidation = response[0];
        });

      });
    });
  }

  getValidations4comparison(): void {
    // return validations available for comparison, given dataset and version
    console.log(this.selectedDatasetModel);
    const parameters = new HttpParams()
      .set('ref_dataset', String(this.selectedDatasetModel[0].datasetModel.selectedDataset.short_name))
      .set('ref_version', String(this.selectedDatasetModel[0].datasetModel.selectedVersion.short_name))
      .set('max_datasets', String(this.maxDatasets));
    console.log(parameters);
    this.validationrunService.getValidationsForComparison(parameters).subscribe(response => {
      if (response){
        this.validations4Comparison = response;
      } else{
        this.validations4Comparison = [];
      }
    });
  }

  selectedValidationChanged(): void {
    // change validation from dropdown menu on click
  }

  addValidation2Comparison(): void {
    // should add the selected validation in the comparisonModel
  }

  removeValidation() {
    // should remove the selected validation from the comparisonModel
  }

  generateExtentOptions(): void {
    // should be expanded to include custom selection, and should have non-fixed default conditions
    this.spatialExtent = new ExtentModel(false, 'Union can only be chosen when the default is Intesection', true, 'Compare the union of spatial extents');
  }

  startComparison() {
    // should start the comparison
  }

  onDatasetChange(): void{
    this.getValidations4comparison();
  }
}

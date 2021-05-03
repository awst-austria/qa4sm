import {Component, OnInit} from '@angular/core';
import {DatasetConfigModel} from "../../../../pages/validate/dataset-config-model";
import {DatasetService} from "../../../core/services/dataset/dataset.service";
import {DatasetVersionService} from "../../../core/services/dataset/dataset-version.service";
import {DatasetComponentSelectionModel} from "../../../dataset/components/dataset/dataset-component-selection-model";
import {Validations2CompareModel} from "./validation-selection.model";
import {ValidationrunService} from "../../../core/services/validation-run/validationrun.service";
import {HttpParams} from "@angular/common/http";
import {ValidationrunDto} from "../../../core/services/validation-run/validationrun.dto";
import {ExtentModel} from "../spatial-extent/extent-model";

const N_MAX_VALIDATIONS = 2 // A maximum of two validation results can be compared, at the moment

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  max_datasets: Number // how to provide a number parameter to HttpParams?
  selectedDatasetModel: DatasetConfigModel[] = [];
  spatialExtent: ExtentModel;
  validations4Comparison: ValidationrunDto[] = [];
  // model that stores all the inputs for the comparison run
  comparisonModel: Validations2CompareModel = new Validations2CompareModel([], true); // how to connect to extent selection?


  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    // you have already created this object in line 17, there is no need to do it one more time
    // this.comparisonModel = new Validations2CompareModel();
    this.addDatasetToSelection();
    this.getValidations4comparison();
    this.generateExtentOptions();
  }

  addDatasetToSelection(): void{
    this.selectDataset(this.selectedDatasetModel);
  }

  private selectDataset(selected: DatasetConfigModel[]): void{
    const model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
    selected.push(model);
    //get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      model.datasetModel.selectedDataset = datasets[0];

      //then get all versions for the first dataset in the result list
      this.versionService.getVersionsByDataset(model.datasetModel.selectedDataset.id).subscribe(versions => {
        model.datasetModel.selectedVersion = versions[0];
      });
    });
  }

  getValidations4comparison(): void {
    // return validations available for comparison, given dataset and version
    const parameters = new HttpParams().set('ref_dataset', String(this.selectedDatasetModel[0].datasetModel.selectedDataset.short_name))
      .set('ref_version', String(this.selectedDatasetModel[0].datasetModel.selectedDataset.short_name));

    this.validationrunService.getValidations4Comparison(parameters).subscribe(response => {
      const validations = response;
      this.validations4Comparison = validations;
    })
    this.comparisonModel.selectedValidations.push(this.validations4Comparison[0])
  }

  addValidationButtonDisabled(): boolean {
    // if the # of selected validations exceeds 2
    return this.comparisonModel.selectedValidations.length >= N_MAX_VALIDATIONS;
  }

  selectedValidationChanged(): void {
    // change validation from dropdown menu on click in this.comparisonModel.selectedValidations
  }

  addValidation2Comparison(): void {
    // should add the selected validation in the comparisonModel
  }

  removeValidation(){
    // should remove the selected validation from the comparisonModel
  }

  generateExtentOptions(): void {
    // should be expanded to include custom selection, and should have non-fixed default conditions
    this.spatialExtent = new ExtentModel(false,"Union can only be chosen when the default is Intesection", true, 'Compare the union of spatial extents');
  }

  startComparison(){
    // should start the comparison
  }
}

import {Component, OnInit} from '@angular/core';
import {DatasetConfigModel} from "../../../../pages/validate/dataset-config-model";
import {DatasetService} from "../../../core/services/dataset/dataset.service";
import {DatasetVersionService} from "../../../core/services/dataset/dataset-version.service";
import {DatasetComponentSelectionModel} from "../../../dataset/components/dataset/dataset-component-selection-model";
import {Validations2CompareModel} from "./validation-selection.model";
import {ValidationrunService} from "../../../core/services/validation-run/validationrun.service";
import {HttpParams} from "@angular/common/http";
import {ValidationrunDto} from "../../../core/services/validation-run/validationrun.dto";

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  max_datasets: Number = 3; // how to provide a number parameter to HttpParams?
  selectedDatasetModel: DatasetConfigModel[] = [];
    // new DatasetConfigModel(null, null, null);
  comparisonModel: Validations2CompareModel = new Validations2CompareModel([]);
  validations4Comparison: ValidationrunDto[] = [];
  selectedValidation: ValidationrunDto;

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private validationrunService: ValidationrunService) { }

  ngOnInit(): void {
    // you have already created this object in line 17, there is no need to do it one more time
    // this.comparisonModel = new Validations2CompareModel();
    this.addDatasetToSelection();
    this.getValidations4comparison();
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

  getValidations4comparison() {
    // return validations available for comparison, given dataset and version
    const parameters = new HttpParams()
      .set('ref_dataset', String(this.selectedDatasetModel[0].datasetModel.selectedDataset?.short_name))
      .set('ref_version', String(this.selectedDatasetModel[0].datasetModel.selectedDataset?.short_name));

    this.validationrunService.getValidations4Comparison(parameters).subscribe(response => {
      const validations = response;
      this.validations4Comparison = validations;
    })
  }

  selectedValidationChanged(): void {
    // change validation from dropdown menu on click
  }

  addValidation2Comparison(): void {
    // should add the selected validation in the comparisonModel
  }

  removeValidation(){
    // should remove the selected validation from the comparisonModel
  }

  startComparison(){
    // should start the comparison
  }
}

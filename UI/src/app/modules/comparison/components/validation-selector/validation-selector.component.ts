import { Component, OnInit } from '@angular/core';
import {DatasetConfigModel} from "../../../../pages/validate/dataset-config-model";
import {DatasetService} from "../../../core/services/dataset/dataset.service";
import {DatasetVersionService} from "../../../core/services/dataset/dataset-version.service";
import {DatasetComponentSelectionModel} from "../../../dataset/components/dataset/dataset-component-selection-model";
import {ValidationResultModel} from "../../../../pages/validation-result/validation-result-model";
import {Validations2CompareModel} from "./validation-selection.model";

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  selectedDatasetModel: DatasetConfigModel = new DatasetConfigModel(null, null, null)
  comparisonModel: Validations2CompareModel = new Validations2CompareModel([])

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService) { }

  ngOnInit(): void {
    this.comparisonModel = new Validations2CompareModel()
    this.addDatasetToSelection()
  }

  addDatasetToSelection(){
    this.selectDataset(this.selectedDatasetModel);
  }

  private selectDataset(selected: DatasetConfigModel) {
    selected = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null);
    //get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      selected.datasetModel.selectedDataset = datasets[0];

      //then get all versions for the first dataset in the result list
      this.versionService.getVersionsByDataset(selected.datasetModel.selectedDataset.id).subscribe(versions => {
        selected.datasetModel.selectedVersion = versions[0];
      });
    });
  }

  private filterValidations(element: ValidationResultModel){
    // function to filter the validations list based on the reference dataset
    return //condition of selected reference dataset and version
  }

  selectedList (allValidations: ValidationResultModel[]){
    // filters all the validations
    return allValidations.filter(this.filterValidations)
  }

  removeValidation(){
    // here function to remove the selected validation
  }
}

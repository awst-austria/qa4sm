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
import {Observable} from "rxjs";

const N_MAX_VALIDATIONS = 2 // A maximum of two validation results can be compared, at the moment - this shouldn't be hardcoded

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  multipleNonReference: boolean = false;
  selectedValidation: ValidationrunDto
  selectedDatasetModel: DatasetConfigModel[] = [];
  spatialExtent: ExtentModel;
  // all the possible validations given filters
  validations4Comparison: ValidationrunDto[] = [];
  // model that stores all the inputs for the comparison run
  comparisonModel: Validations2CompareModel = new Validations2CompareModel([], true); // how to connect to extent selection?

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    // console.log(this.multipleNonReference)
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
        // console.log(parameters);

        this.validationrunService.getValidationsForComparison(parameters).subscribe(response => {
          // console.log(validations);
          // console.log(response);
          this.validations4Comparison = response;
          if (response) {
            this.selectedValidation = response[0];  // problem initializing this
          }
        });
      });
    });
  }

  getValidations4comparison(): void {
    // return validations available for comparison, given dataset and version
    // console.log('the dataset selection is:', this.checkbox2NonReferenceNumber(this.multipleNonReference))
    const parameters = new HttpParams()
      .set('ref_dataset', String(this.selectedDatasetModel[0].datasetModel.selectedDataset.short_name))
      .set('ref_version', String(this.selectedDatasetModel[0].datasetModel.selectedVersion.short_name))
      // number of non-reference datasets
      .set('max_datasets', String(this.checkbox2NonReferenceNumber()));
    // console.log(parameters);
    this.validationrunService.getValidationsForComparison(parameters).subscribe(response => {
      if (response){
        this.validations4Comparison = response;
      } else{
        this.validations4Comparison = [];
      }
    });
  }

  multipleNonReferenceChange(): void {
    // reinitialize list when checkbox value is changed
    this.getValidations4comparison()
  }

  checkbox2NonReferenceNumber(){
    // convert the checkbox boolean selection to number of non-references
    this.comparisonModel.selectedValidations = []  // empty the selection in case the button is clicked
    if (this.multipleNonReference){
      return 2
    }
    return 1
  }

  addValidationButtonDisabled(): boolean {
    // if the checkbox has been toggled - this shouldn't be hardcoded
    if (this.multipleNonReference){
      return this.comparisonModel.selectedValidations.length >= 1;
    }
    // if not
    return this.comparisonModel.selectedValidations.length >= N_MAX_VALIDATIONS;
  }

  addValidation2Comparison(): void {
    // should add the selected validation in the comparisonModel
    // console.log(this.comparisonModel.selectedValidations)
    console.log(this.selectedValidation)
    this.comparisonModel.selectedValidations.push(this.selectedValidation)
  }

  removeValidation(target: ValidationrunDto) {
    // should remove the selected validation from the comparisonModel
    console.log(this.comparisonModel.selectedValidations)
    let toBeRemoved = this.comparisonModel.selectedValidations.indexOf(target);
    this.comparisonModel.selectedValidations.splice(toBeRemoved, 1);
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

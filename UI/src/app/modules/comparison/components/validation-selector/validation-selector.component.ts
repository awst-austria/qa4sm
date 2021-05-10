import {Component, OnInit, Output, EventEmitter} from '@angular/core';
import {DatasetConfigModel} from '../../../../pages/validate/dataset-config-model';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';
import {Validations2CompareModel} from './validation-selection.model';
import {ValidationrunService} from '../../../core/services/validation-run/validationrun.service';
import {HttpParams} from '@angular/common/http';
import {ValidationrunDto} from '../../../core/services/validation-run/validationrun.dto';
import {ExtentModel} from '../spatial-extent/extent-model';

const N_MAX_VALIDATIONS = 2 // A maximum of two validation results can be compared, at the moment - this shouldn't be hardcoded

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  @Output() emitComparisonInput = new EventEmitter<Validations2CompareModel>();

  multipleNonReference: boolean = false;
  selectedValidation: ValidationrunDto
  selectedDatasetModel: DatasetConfigModel[] = [];
  // initialize the extent model with a default intersection configuration
  spatialExtent: ExtentModel = new ExtentModel(true);
  // all the possible validations given filters
  validations4Comparison: ValidationrunDto[] = [];
  // model that stores all the inputs for the comparison run
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [],
    new ExtentModel(true).getIntersection,
  );

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    // console.log(this.multipleNonReference)
    // this.comparisonModel = new Validations2CompareModel();
    this.addDatasetToSelection();
    this.comparisonModel.getIntersection = this.checkOverlapping();
  }

  addDatasetToSelection(): void {
    this.selectDataset(this.selectedDatasetModel);
  }

  onDatasetChange(): void{
    this.getValidations4comparison();
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
    // console.log('selected validation', this.selectedValidation)
    this.comparisonModel.selectedValidations.push(this.selectedValidation)
    this.comparisonModel.getIntersection = this.checkOverlapping()
  }

  removeValidation(target: ValidationrunDto) {
    // should remove the selected validation from the comparisonModel
    // console.log(this.comparisonModel.selectedValidations)
    let toBeRemoved = this.comparisonModel.selectedValidations.indexOf(target);
    this.comparisonModel.selectedValidations.splice(toBeRemoved, 1);
    this.comparisonModel.getIntersection = this.checkOverlapping();
  }

  checkOverlapping(): boolean {
    // check that the two selected validations have overlapping extents
    if (this.comparisonModel.selectedValidations.length > 1) {  // two validations selected
      let val1 = this.comparisonModel.selectedValidations[0];
      let val2 = this.comparisonModel.selectedValidations[1];
      // condition for intersection:
      return !(val1.max_lon < val2.min_lon || val1.min_lon > val2.max_lon || val1.min_lat > val2.max_lat || val1.max_lat < val2.min_lat)
    } else {  // only one validation selected. Return 'false' to workaround
      return false
    }
  }

  spatialExtentDisabled(): boolean {
    // check conditions for union selection checkbox
    if (this.multipleNonReference) { return true } else {
      // console.log('overlapping', this.checkOverlapping())
     return !this.checkOverlapping();
    }
  }

  unionChecked(isNotChecked: boolean) {
    // should be true when checkbox is unchecked, and vice-versa
    this.comparisonModel.getIntersection = isNotChecked;
  }

  startComparison() {
    // should start the comparison
    // console.log(this.comparisonModel)
    this.emitComparisonInput.emit(this.comparisonModel)
  }
}

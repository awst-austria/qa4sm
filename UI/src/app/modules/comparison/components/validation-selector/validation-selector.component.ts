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
import {ComparisonService} from '../../services/comparison.service';
import {ToastService} from '../../../core/services/toast/toast.service';

const N_MAX_VALIDATIONS = 2; // A maximum of two validation results can be compared, at the moment - this shouldn't be hardcoded

@Component({
  selector: 'qa-validation-selector',
  templateUrl: './validation-selector.component.html',
  styleUrls: ['./validation-selector.component.scss']
})
export class ValidationSelectorComponent implements OnInit {

  multipleNonReference = false;
  selectValidationLabel: string;
  selectedValidation: ValidationrunDto;
  selectedDatasetModel: DatasetConfigModel[] = [];
  // initialize the extent model with a default intersection configuration
  spatialExtent: ExtentModel = new ExtentModel(true);
  // all the possible validations given filters
  validations4Comparison: ValidationrunDto[] = [];
  // model that stores all the inputs for the comparison run
  comparisonModel: Validations2CompareModel = new Validations2CompareModel(
    [],
    new ExtentModel(true).getIntersection,
    this.multipleNonReference
  );

  constructor(private datasetService: DatasetService,
              private versionService: DatasetVersionService,
              private validationrunService: ValidationrunService,
              private comparisonService: ComparisonService,
              private toastService: ToastService) {
  }

  ngOnInit(): void {
    // this.comparisonModel = new Validations2CompareModel();
    this.comparisonService.currentComparisonModel.subscribe(model => this.comparisonModel = model);
    this.addDatasetToSelection();
    this.comparisonModel.getIntersection = this.checkOverlapping();
    this.comparisonModel.multipleNonReference = this.multipleNonReference;
  }

  addDatasetToSelection(): void {
    this.selectDataset(this.selectedDatasetModel);
  }

  onDatasetChange(): void{
    this.getValidations4comparison();
  }

  private selectDataset(selected: DatasetConfigModel[]): void {
    const model = new DatasetConfigModel(new DatasetComponentSelectionModel(null, null, null), null, null, null);
    selected.push(model);
    // get all datasets
    this.datasetService.getAllDatasets().subscribe(datasets => {
      model.datasetModel.selectedDataset = datasets.find(dataset => dataset.short_name === 'ISMN');
      this.selectValidationLabel = 'Wait for validations to be loaded';
      // then get all versions for the first dataset in the result list
      this.versionService.getVersionsByDataset(model.datasetModel.selectedDataset.id).subscribe(versions => {
        model.datasetModel.selectedVersion = versions[0];
        this.getValidations4comparison(String( model.datasetModel.selectedDataset.short_name),
          String(model.datasetModel.selectedVersion.short_name));
      });
    });
  }

  getValidations4comparison(refDataset?, refVersion?): void{
    if (!refDataset && !refVersion){
      refDataset = String(this.selectedDatasetModel[0].datasetModel.selectedDataset.short_name);
      refVersion = String(this.selectedDatasetModel[0].datasetModel.selectedVersion.short_name);
    }
    const parameters = new HttpParams()
      .set('ref_dataset', refDataset)
      .set('ref_version', refVersion)
      // number of non-reference datasets
      .set('max_datasets', String(this.checkbox2NonReferenceNumber()));
    this.selectValidationLabel = 'Wait for validations to be loaded';
    this.validationrunService.getValidationsForComparison(parameters).subscribe(response => {
      if (response){
        this.validations4Comparison = response;
        this.selectedValidation = response[0];
        this.selectValidationLabel = 'Select a validation';
      } else{
        this.validations4Comparison = [];
        this.selectValidationLabel = 'There are no validations available';
      }
    });

  }

  multipleNonReferenceChange(): void {
    // reinitialize list when checkbox value is changed
    this.getValidations4comparison();
  }

  checkbox2NonReferenceNumber(): number{
    // convert the checkbox boolean selection to number of non-references
    this.comparisonModel.selectedValidations = []; // empty the selection in case the button is clicked
    if (this.multipleNonReference){
      return 2;
    }
    return 1;
  }

  addValidationButtonDisabled(): boolean {
    // if the checkbox has been toggled - this shouldn't be hardcoded
    if (this.multipleNonReference){
      return this.comparisonModel.selectedValidations.length >= 1;
    }

    // if not
    return !(this.comparisonModel.selectedValidations.length < N_MAX_VALIDATIONS && this.validations4Comparison.length > 0);
  }

  addValidation2Comparison(): void {
    // should add the selected validation in the comparisonModel
    this.comparisonModel.selectedValidations.push(this.selectedValidation);
    this.comparisonModel.getIntersection = this.checkOverlapping();
    this.comparisonModel.multipleNonReference = this.multipleNonReference;
  }

  removeValidation(target: ValidationrunDto): void {
    // should remove the selected validation from the comparisonModel
    const toBeRemoved = this.comparisonModel.selectedValidations.indexOf(target);
    this.comparisonModel.selectedValidations.splice(toBeRemoved, 1);
    this.comparisonModel.getIntersection = this.checkOverlapping();
    this.comparisonModel.multipleNonReference = this.multipleNonReference;
    this.comparisonService.sendComparisonModel(this.comparisonModel);
  }

  checkOverlapping(): boolean {
    // check that the two selected validations have overlapping extents
    if (this.comparisonModel.selectedValidations.length > 1) {  // two validations selected
      const val1 = this.comparisonModel.selectedValidations[0];
      const val2 = this.comparisonModel.selectedValidations[1];
      // condition for intersection:
      return !(val1.max_lon < val2.min_lon || val1.min_lon > val2.max_lon || val1.min_lat > val2.max_lat || val1.max_lat < val2.min_lat);
    } else {  // only one validation selected. Return 'false' to workaround
      return false;
    }
  }

  spatialExtentDisabled(): boolean {
    // check conditions for union selection checkbox
    if (this.multipleNonReference) {
      return true;
    } else {
     return !this.checkOverlapping();
    }
  }

  unionChecked(isNotChecked: boolean): void {
    // should be true when checkbox is unchecked, and vice-versa
    this.comparisonModel.getIntersection = isNotChecked;
  }

  startComparison(): void{
    // should start the comparison
    if (this.comparisonModel.selectedValidations.length === 0 ||
      (this.comparisonModel.selectedValidations.length === 1 && !this.comparisonModel.multipleNonReference)) {
      this.toastService.showErrorWithHeader('Nothing to compare', 'Add two validations or check  ' +
        '"Multiple non-reference datasets" and add one validation to start comparison.');
    } else {
      this.comparisonService.sendComparisonModel(this.comparisonModel);
    }
  }
}

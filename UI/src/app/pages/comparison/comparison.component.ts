import {Component, OnInit} from '@angular/core';
import {
  Validations2CompareModel
} from '../../modules/comparison/components/validation-selector/validation-selection.model';
import {ComparisonService} from '../../modules/comparison/services/comparison.service';
import {ToastService} from '../../modules/core/services/toast/toast.service';

@Component({
    selector: 'qa-comparison',
    templateUrl: './comparison.component.html',
    styleUrls: ['./comparison.component.scss'],
    standalone: false
})
export class ComparisonComponent implements OnInit {
  comparisonModel: Validations2CompareModel;
  showComparisonResults = false;

  constructor(private comparisonService: ComparisonService,
              private toastService: ToastService) {
  }

  isError = false;

  ngOnInit(): void {
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      this.comparisonModel = comparison;
      if (this.comparisonModel.selectedValidations.length !== 0) {
        const cond1 = comparison.selectedValidations[0].dataset_configurations.length > 2
          && this.comparisonModel.selectedValidations.length === 1;
        const cond2 = comparison.selectedValidations[0].dataset_configurations.length === 2
          && this.comparisonModel.selectedValidations.length === 2;
        this.showComparisonResults = cond1 || cond2;
      } else {
        this.showComparisonResults = false;
      }
    });
  }

  handleError(event): void {
    if (!this.isError && event) {
      this.isError = event;
      this.toastService.showErrorWithHeader(
        'Comparison results not available',
        'Some of the comparison results are not available, because the chosen validations are too large to be processed on the fly.',
        7000);
    }
  }
}

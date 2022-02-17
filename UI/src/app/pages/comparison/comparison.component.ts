import {Component, OnInit} from '@angular/core';
import {
  Validations2CompareModel
} from '../../modules/comparison/components/validation-selector/validation-selection.model';
import {ComparisonService} from '../../modules/comparison/services/comparison.service';

@Component({
  selector: 'qa-comparison',
  templateUrl: './comparison.component.html',
  styleUrls: ['./comparison.component.scss']
})
export class ComparisonComponent implements OnInit {
  comparisonModel: Validations2CompareModel;
  showComparisonResults = false;
  constructor(private comparisonService: ComparisonService) { }

  ngOnInit(): void {
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      this.comparisonModel = comparison;
      if (this.comparisonModel.selectedValidations.length !== 0){
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
}

import {Component, OnInit} from '@angular/core';
import {Validations2CompareModel} from '../../modules/comparison/components/validation-selector/validation-selection.model';
import {ComparisonService} from '../../modules/comparison/services/comparison.service';

@Component({
  selector: 'qa-comparison',
  templateUrl: './comparison.component.html',
  styleUrls: ['./comparison.component.scss']
})
export class ComparisonComponent implements OnInit {
  comparisonModel: Validations2CompareModel;
  constructor(private comparisonService: ComparisonService) { }

  ngOnInit(): void {
    this.comparisonService.currentComparisonModel.subscribe(comparison => {
      this.comparisonModel = comparison;
    });
  }
}

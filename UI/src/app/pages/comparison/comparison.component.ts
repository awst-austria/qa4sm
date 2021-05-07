import { Component, OnInit } from '@angular/core';
import {Validations2CompareModel} from "../../modules/comparison/components/validation-selector/validation-selection.model";

@Component({
  selector: 'qa-comparison',
  templateUrl: './comparison.component.html',
  styleUrls: ['./comparison.component.scss']
})
export class ComparisonComponent implements OnInit {

  selectedComparisonConfiguration: Validations2CompareModel;

  constructor() { }

  ngOnInit(): void {
  }

  provideConfiguration(configuration: Validations2CompareModel): void {
    this.selectedComparisonConfiguration = configuration
  }
}

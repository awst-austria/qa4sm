import { Component, Input, OnInit } from '@angular/core';
import { FilterModel } from '../basic-filter/filter-model';
import { BehaviorSubject } from 'rxjs';
import { DatasetComponentSelectionModel } from '../../../dataset/components/dataset/dataset-component-selection-model';

@Component({
    selector: 'qa-threshold-filter',
    templateUrl: './threshold-filter.component.html',
    styleUrls: ['./threshold-filter.component.scss'],
    standalone: false
})
export class ThresholdFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;
  @Input() minThreshold: number = 0.;
  @Input() maxThreshold: number = 1.;
  @Input() increment: number = 0.05;
  @Input() units: string = "fraction";
  maxFractionDigits = 2; // if needed, make it input value

  editThreshold = "0";

  constructor() {
  }

  ngOnInit(): void {
    this.filterModel$.subscribe(model => {
      if (model != null) {
        this.initComponent();
      }
    });
  }

  private initComponent(): void {
    this.editThreshold = this.filterModel$.value.filterDto.default_parameter;
    this.filterModel$.value.parameters$.subscribe(param => this.editThreshold = param);
  }

  public saveNewValue(event): void {
    this.filterModel$.value.parameters$.next(event.value.toFixed(this.maxFractionDigits));
  }
}

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FilterModel } from '../basic-filter/filter-model';
import { DatasetComponentSelectionModel } from '../../../dataset/components/dataset/dataset-component-selection-model';

@Component({
  selector: 'qa-ismn-depth-filter',
  templateUrl: './ismn-depth-filter.component.html',
  styleUrls: ['./ismn-depth-filter.component.scss'],
  standalone: false,
})
export class IsmnDepthFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;
  @Output() depthSelectionChanged = new EventEmitter<string>();

  dialogVisible = false;

  editFrom = 0;
  editTo = 0;

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
    this.updateUiFields(this.filterModel$.value.filterDto.default_parameter);
    // this.filterModel$.subscribe(() => this.initFilterFieldSubscriptions());
    this.initFilterFieldSubscriptions();
  }

  private initFilterFieldSubscriptions(): void {
    this.filterModel$.value.parameters$.subscribe(param => this.updateUiFields(param));
  }

  private updateUiFields(parameters: string): void {
    const values = parameters.split(',');
    this.editFrom = Number(values[0]);
    this.editTo = Number(values[1]);
  }

  public saveNewValues(): void {
    this.filterModel$.value.parameters$.next(this.editFrom + ',' + this.editTo);
    this.dialogVisible = false;
    this.depthSelectionChanged.emit(this.editFrom + ";" + this.editTo);
  }
}

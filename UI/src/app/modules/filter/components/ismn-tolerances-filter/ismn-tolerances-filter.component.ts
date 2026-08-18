import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {FilterModel} from '../basic-filter/filter-model';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';

@Component({
    selector: 'qa-ismn-tolerances-filter',
    templateUrl: './ismn-tolerances-filter.component.html',
    styleUrls: ['./ismn-tolerances-filter.component.scss'],
    standalone: false
})
export class IsmnTolerancesFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;
  @Output() tolerancesSelectionChanged = new EventEmitter<string>();

  dialogVisible = false;

  editTop = 0;
  editBottom = 0;

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
    this.initFilterFieldSubscriptions();
  }

  private initFilterFieldSubscriptions(): void {
    this.filterModel$.value.parameters$.subscribe(param => this.updateUiFields(param));
  }

  private updateUiFields(parameters: string): void {
    const values = parameters.split(',');
    this.editTop = Number(values[0]);
    this.editBottom = Number(values[1]);
  }

  // toggling the checkbox activates/deactivates ISMN sensor merging
  public toggleEnabled(enabled: boolean): void {
    this.filterModel$.value.enabled = enabled;
    this.tolerancesSelectionChanged.emit(this.editTop + ';' + this.editBottom);
  }

  public saveNewValues(): void {
    this.filterModel$.value.parameters$.next(this.editTop + ',' + this.editBottom);
    this.dialogVisible = false;
    this.tolerancesSelectionChanged.emit(this.editTop + ';' + this.editBottom);
  }
}

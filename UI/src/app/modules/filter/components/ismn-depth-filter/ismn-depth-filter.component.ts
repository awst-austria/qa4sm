import {Component, Input, OnInit} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {FilterModel} from '../basic-filter/filter-model';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';

@Component({
  selector: 'qa-ismn-depth-filter',
  templateUrl: './ismn-depth-filter.component.html',
  styleUrls: ['./ismn-depth-filter.component.scss']
})
export class IsmnDepthFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;

  dialogVisible = false;

  constructor() {
  }

  ngOnInit(): void {
    console.log(this.filterModel$.value.parameters$.value);
  }
}

import {Component, Input, OnInit} from '@angular/core';
import {FilterModel} from '../basic-filter/filter-model';
import {TreeNode} from 'primeng/api';


@Component({
  selector: 'qa-ismn-network-filter',
  templateUrl: './ismn-network-filter.component.html',
  styleUrls: ['./ismn-network-filter.component.scss']
})
export class IsmnNetworkFilterComponent implements OnInit {

  @Input() filterModel: FilterModel;

  networkSelectorVisible: boolean = false;

  networkTree: TreeNode;

  constructor() {
  }

  ngOnInit(): void {
  }

  cucc() {
    this.networkSelectorVisible = true;
  }
}

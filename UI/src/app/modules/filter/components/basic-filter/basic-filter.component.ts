import {Component, Input, OnInit} from '@angular/core';
import {FilterModel} from './filter-model';

@Component({
  selector: 'qa-basic-filter',
  templateUrl: './basic-filter.component.html',
  styleUrls: ['./basic-filter.component.scss']
})
export class BasicFilterComponent implements OnInit {

  @Input() filterModel: FilterModel;

  constructor() {
  }

  ngOnInit(): void {
  }
}

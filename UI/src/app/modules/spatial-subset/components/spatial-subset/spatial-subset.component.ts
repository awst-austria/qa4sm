import {Component, Input, OnInit} from '@angular/core';
import {SpatialSubsetModel} from './spatial-subset-model';

@Component({
  selector: 'qa-spatial-subset',
  templateUrl: './spatial-subset.component.html',
  styleUrls: ['./spatial-subset.component.scss']
})
export class SpatialSubsetComponent implements OnInit {

  @Input() subsetModel:SpatialSubsetModel=new SpatialSubsetModel();
  constructor() {

  }

  ngOnInit(): void {
  }

}

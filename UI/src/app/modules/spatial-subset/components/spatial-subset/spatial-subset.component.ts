import {Component, Input, OnInit} from '@angular/core';
import {SpatialSubsetModel} from './spatial-subset-model';

@Component({
  selector: 'qa-spatial-subset',
  templateUrl: './spatial-subset.component.html',
  styleUrls: ['./spatial-subset.component.scss']
})
export class SpatialSubsetComponent implements OnInit {

  @Input() subsetModel: SpatialSubsetModel;

  constructor() {
  }

  ngOnInit(): void {
  }

  clearCoordinates() {
    this.subsetModel.maxLat$.next(null);
    this.subsetModel.maxLon$.next(null);
    this.subsetModel.minLat$.next(null);
    this.subsetModel.minLon$.next(null);
  }

}

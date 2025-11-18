import {Component, Input} from '@angular/core';
import {SpatialSubsetModel} from './spatial-subset-model';

@Component({
    selector: 'qa-spatial-subset',
    templateUrl: './spatial-subset.component.html',
    styleUrls: ['./spatial-subset.component.scss'],
    standalone: false
})
export class SpatialSubsetComponent {

  @Input() subsetModel: SpatialSubsetModel;

  constructor() {
  }

  clearCoordinatesOrSetDefault(): void{
    if (!this.subsetModel.limited$.getValue()){
      this.subsetModel.maxLat$.next(null);
      this.subsetModel.maxLon$.next(null);
      this.subsetModel.minLat$.next(null);
      this.subsetModel.minLon$.next(null);
    } else {
      this.subsetModel.maxLat$.next(this.subsetModel.maxLatLimit$.getValue());
      this.subsetModel.maxLon$.next(this.subsetModel.maxLonLimit$.getValue());
      this.subsetModel.minLat$.next(this.subsetModel.minLatLimit$.getValue());
      this.subsetModel.minLon$.next(this.subsetModel.minLonLimit$.getValue());
    }

  }

  checkValIfLimited(value: number, checkMinMax = false): any{
    if (this.subsetModel.limited$.getValue() || checkMinMax){
      return value;
    }
  }
}

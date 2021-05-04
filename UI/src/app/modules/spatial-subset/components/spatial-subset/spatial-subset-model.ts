import {NewValidationRunSpatialSubsettingDto} from '../../../../pages/validate/service/new-validation-run-spatial-subsetting-dto';
import {BehaviorSubject} from 'rxjs';

export class SpatialSubsetModel {
  constructor(public maxLat$: BehaviorSubject<number>,
              public maxLon$: BehaviorSubject<number>,
              public minLat$: BehaviorSubject<number>,
              public minLon$: BehaviorSubject<number>) {
  }

  public toNewValSpatialSubsettingDto(): NewValidationRunSpatialSubsettingDto {
    return new NewValidationRunSpatialSubsettingDto(this.minLat$.getValue(), this.minLon$.getValue(), this.maxLat$.getValue(), this.maxLon$.getValue());
  }

  public setValues(newMaxLat: number, newMaxLon: number, newMinLat: number, newMinLon: number): void{
    this.maxLat$.next(newMaxLat);
    this.maxLon$.next(newMaxLon);
    this.minLat$.next(newMinLat);
    this.minLon$.next(newMinLon);
  }
}

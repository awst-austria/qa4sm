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
}

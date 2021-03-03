import {NewValidationRunSpatialSubsettingDto} from '../../../../pages/validate/service/new-validation-run-spatial-subsetting-dto';

export class SpatialSubsetModel {
  constructor(public maxLat?: number,
              public maxLon?: number,
              public minLat?: number,
              public minLon?: number) {
  }

  public toNewValSpatialSubsettingDto(): NewValidationRunSpatialSubsettingDto {
    return new NewValidationRunSpatialSubsettingDto(this.minLat, this.minLon, this.maxLat, this.maxLon);
  }
}

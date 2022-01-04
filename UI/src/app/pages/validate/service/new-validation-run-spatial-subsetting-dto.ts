export class NewValidationRunSpatialSubsettingDto {
  constructor(public min_lat?: number,
              public min_lon?: number,
              public max_lat?: number,
              public max_lon?: number) {
  }
}

export class ExtentModel {
  constructor(public value: boolean,
              public helperText: string,
              public disabled: boolean,  // needed to force 'union' comparison when extents are non-overlapping
              public description: string) {
  }
}

// should be expanded when custom spatial extent can be selected

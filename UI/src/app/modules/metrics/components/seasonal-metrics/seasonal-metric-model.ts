export class SeasonalMetricModel {
  constructor(public metricName: string,
              public type: string,
              public description: string,
              public overlap: number) {
  }
}

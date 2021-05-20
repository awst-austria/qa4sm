export class AnomaliesModel {
  constructor(public method: string,
              public description: string,
              public anomaliesFrom?: Date,
              public anomaliesTo?: Date) {
  }
}

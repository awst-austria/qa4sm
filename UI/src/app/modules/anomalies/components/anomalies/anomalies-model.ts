export class AnomaliesModel {

  constructor(public id: string,
              public description: string,
              public anomaliesFrom?: Date,
              public anomaliesTo?: Date) {
  }
}

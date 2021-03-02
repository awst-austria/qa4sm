export class NewValidationRunAnomaliesDto {
  constructor(public method: string,
              public anomalies_from?: Date,
              public anomalies_to?: Date) {
  }
}

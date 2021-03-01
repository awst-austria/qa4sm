export class DatasetConfigurationDto {
  constructor(
    public id: number,
    public validation: string,
    public dataset: number,
    public version: number,
    public variable: number,
    public filters: number[],
    public parametrised_filters: number[]
  ) {
  }
}

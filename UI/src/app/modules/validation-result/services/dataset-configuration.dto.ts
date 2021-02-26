export class ConfigurationDto {
  constructor(
    public validation: number,
    public dataset: number,
    public version: number,
    public variable: number,
    public filters: number[],
    public parametrised_filters: number[]
  ) {
  }
}

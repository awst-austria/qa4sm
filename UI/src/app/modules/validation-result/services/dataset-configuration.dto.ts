export class DatasetConfigurationDto {
  constructor(
    public id: number,
    public validation: string,
    public dataset: number,
    public version: number,
    public variable: number,
    public filters: number[],
    public parametrised_filters: number[],
    public parametrisedfilter_set: number[],
    public is_spatial_reference: boolean,
    public is_temporal_reference: boolean,
    public is_scaling_reference: boolean
  ) {
  }
}

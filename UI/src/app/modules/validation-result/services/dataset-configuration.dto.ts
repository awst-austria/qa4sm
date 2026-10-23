export interface MergedLayerDto {
  id: number;
  short_name: string;
  depth_from: number;
  depth_to: number;
}

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
    public is_scaling_reference: boolean,
    // Computed server-side. `variable` alone is not enough to describe a
    // merged run: it holds only the shallowest contributing layer, and the
    // DataVariable unit is the raw kg/m² rather than the m³/m³ a merged GLDAS
    // series actually holds. Take the unit from here, not from a lookup.
    public variable_unit?: string,
    public merged_layers?: MergedLayerDto[],
    public merge_depth_label?: string,
    public merge_weighted?: boolean
  ) {
  }
}

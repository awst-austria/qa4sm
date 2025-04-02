export interface ValidationRunConfigDto {
  dataset_configs: ValidationRunDatasetConfigDto[];
  spatial_reference_config?: ValidationRunDatasetConfigDto;
  temporal_reference_config?: ValidationRunDatasetConfigDto;
  scaling_reference_config?: ValidationRunDatasetConfigDto;
  interval_from?: Date;
  interval_to?: Date;
  min_lat?: number;
  min_lon?: number;
  max_lat?: number;
  max_lon?: number;
  metrics: ValidationRunMetricConfigDto[];
  intra_annual_metrics: IntraAnnualMetricsDto;
  anomalies_method: string;
  anomalies_from?: Date;
  anomalies_to?: Date;
  scaling_method: string;
  scale_to: string;
  name_tag: string;
  temporal_matching: number;
  changes?: ConfigurationChanges;
}

export interface ValidationRunDatasetConfigDto {
  dataset_id: number;
  version_id: number;
  variable_id: number;
  basic_filters: number[];
  parametrised_filters: ParametrisedFilterConfig[];
  is_spatial_reference: boolean;
  is_temporal_reference: boolean;
  is_scaling_reference: boolean;

}

export interface ValidationRunMetricConfigDto {
  id: string;
  value: boolean;
}

export interface ParametrisedFilterConfig {
  id: number;
  parameters: string;
}

export interface ConfigurationChanges {
  filters: {dataset: string, filter_desc: string[]}[];
  anomalies: boolean;
  scaling: boolean;
  versions: {version: string, dataset: string}[];
  variables: {variable: string, dataset: string}[];
}

export interface IntraAnnualMetricsDto{
  intra_annual_metrics: boolean;
  intra_annual_type: string;
  intra_annual_overlap: number;
}

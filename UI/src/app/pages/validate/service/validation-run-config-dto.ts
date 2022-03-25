export interface ValidationRunConfigDto {
  dataset_configs: ValidationRunDatasetConfigDto[];
  reference_config: ValidationRunDatasetConfigDto;
  interval_from?: Date;
  interval_to?: Date;
  min_lat?: number;
  min_lon?: number;
  max_lat?: number;
  max_lon?: number;
  metrics: ValidationRunMetricConfigDto[];
  anomalies_method: string;
  anomalies_from?: Date;
  anomalies_to?: Date;
  scaling_method: string;
  scale_to: string;
  name_tag: string;
  changes?: ConfigurationChanges;
}

export interface ValidationRunDatasetConfigDto {
  dataset_id: number;
  version_id: number;
  variable_id: number;
  basic_filters: number[];
  parametrised_filters: ParametrisedFilterConfig[];

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
}

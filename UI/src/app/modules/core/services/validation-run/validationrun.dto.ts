export class ValidationrunDto{
  constructor(public id: any,
              public name_tag: string,
              public user: number,
              public start_time: Date,
              public end_time: Date,
              public ok_points: number,
              public total_points: number,
              public error_points: number,
              public progress: number,
              public dataset_configurations: number[],
              public spatial_reference_configuration: number,
              public scaling_ref: number,
              public scaling_method: string,
              public interval_from: Date,
              public interval_to: Date,
              public anomalies: string,
              public min_lat: number,
              public min_lon: number,
              public max_lat: number,
              public max_lon: number,
              public anomalies_from: Date,
              public anomalies_to: Date,
              public output_file: string,
              public is_archived: boolean,
              public last_extended: string,
              public expiry_notified: boolean,
              public doi: string,
              public publishing_in_progress: boolean,
              public tcol: boolean,
              public expiry_date: Date,
              public is_near_expiry: boolean,
              public is_unpublished: boolean,
              public output_dir_url: string,
              public output_file_name: string,
              public copied_run: number[],
              public is_a_copy: boolean,
              public bootstrap_tcol_cis: boolean,
              public temporal_matching: number,
              public comparison_label?: string) {
  }
}


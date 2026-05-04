import {Observable} from "rxjs";
import {PlotDto} from "../global/plot.dto";


export interface BoxplotDict {
  ind: number;
  name: string;
  file: string;
  overview_files: string[];
}

export interface MetricsPlotsDto {
  ind: number;
  metric_query_name: string;
  metric_pretty_name: string;
  boxplot_type: string;  // 'classification' | 'dataset_combination'
  boxplot_dicts: BoxplotDict[];
  overview_files: string[];
  metadata_files: string[];
  comparison_boxplot: any;
  zarr_metrics: any;
  zarr_var_list: string[];
  datasets: string[];
  tsplot_file?: string[];  // for spatial validation
  // computed observables
  boxplotFiles?: Observable<PlotDto[]>;
  overviewFiles?: Observable<PlotDto[]>;
  comparisonFile?: Observable<PlotDto[]>;
  tsplotFiles?: Observable<PlotDto[]>;
}
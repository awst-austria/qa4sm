import {Observable} from "rxjs";
import {PlotDto} from "../global/plot.dto";

export interface MetricsPlotsDto {
  ind: number,
  metric_query_name: string,
  metric_pretty_name: string,
  boxplot_dicts: [{
    ind: number,
    name: string,
    file: string
  }],
  overview_files: string[],
  metadata_files: string[],
  comparison_boxplot: string[],
  datasets: string[],
  boxplotFiles?: Observable<PlotDto[]>,
  overviewFiles?: Observable<PlotDto[]>
  comparisonFile?: Observable<PlotDto[] | null>
}

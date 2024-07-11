import {Observable} from "rxjs";
import {PlotDto} from "../global/plot.dto";

export interface MetricsPlotsDto {
  metric_query_name: string,
  metric_pretty_name: string,
  boxplot_dicts: [{
    ind: number,
    name: string,
    file: string
  }],
  overview_files: string[],
  metadata_files: string[],
  ind: number,
  datasets: string[],
  boxplotFiles?: Observable<PlotDto[]>,
  overviewFiles?: Observable<PlotDto[]>
}

export class MetricsPlotsDto{
  constructor(public metric_query_name: string,
              public metric_pretty_name: string,
              public boxplot_file: string,
              public overview_files: string[],
              public metadata_files: string[],
              public ind: number,
              public datasets: string[]) {
  }
}

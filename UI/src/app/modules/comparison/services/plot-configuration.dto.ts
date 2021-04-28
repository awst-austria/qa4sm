export class PlotConfigurationDto {
  constructor(public comparison: string, // actually not string but python class - possible?
              public plot_type: string,
              public metric: string,) {
  }
}

export class ParameterisedFilterDto{
  constructor(public id: number,
              public dataset_config_id: number,
              public filter_id: number,
              public parameters: string) {
  }
}

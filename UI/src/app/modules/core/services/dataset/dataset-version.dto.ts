export class DatasetVersionDto {
  constructor(
    public id: number,
    public short_name: string,
    public pretty_name: string,
    public help_text: string,
    public time_range_start: Date,
    public time_range_end: Date,
    public geographical_range: object,
  ) {
  }
}

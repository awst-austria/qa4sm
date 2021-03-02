export class NewValRunDatasetConfigDto {
  constructor(public dataset_id: number,
              public version_id: number,
              public variable_id: number,
              public basic_filters: number[]) {
  }

}

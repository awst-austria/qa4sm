export class DatasetDto {
  constructor(public id: number,
              public short_name: string,
              public pretty_name: string,
              public help_text: string,
              public storage_path: string,
              public detailed_description: string,
              public source_reference: string,
              public citation: string,
              public is_only_reference: boolean,
              public versions: number[],
              public variables: number[],
              public filters: number[]) {
  }
}

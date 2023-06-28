export class DatasetDto {
  constructor(public id: number,
              public short_name: string,
              public pretty_name: string,
              public help_text: string,
              public storage_path: string,
              public detailed_description: string,
              public source_reference: string,
              public citation: string,
              public is_spatial_reference: boolean,
              public versions: number[],
              public variables: number[],
              public filters: number[],
              public not_as_reference: boolean,
              public user: string,
              public is_shared: boolean) {
  }
}

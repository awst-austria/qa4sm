export class UserDataFileDto {
  constructor(public id: string,
              public file: File,
              public file_name: string,
              public owner: number,
              public dataset: number,
              public version: number,
              public variable: number,
              public lat_name: string,
              public lon_name: string,
              public time_name: string,
              public all_variables: [{name: string, standard_name: string, long_name: string}],
              public upload_date: Date,
              public is_used_in_validation: boolean
              ) {
  }
}

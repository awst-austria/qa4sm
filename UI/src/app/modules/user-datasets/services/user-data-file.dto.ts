export class UserDataFileDto {
  constructor(public id: string,
              public file: File,
              public file_name: string,
              public owner: number,
              public dataset: number,
              public version: number,
              public variable: number,
              public latname: string,
              public lonname: string,
              public timename: string,
              public variable_choices: [{variable: string, standard_name: string, long_name: string}],
              public lon_name_choices: [{name: string}],
              public lat_name_choices: [{name: string}],
              public time_name_choices: [{name: string}],
              public upload_date: Date
              ) {
  }
}

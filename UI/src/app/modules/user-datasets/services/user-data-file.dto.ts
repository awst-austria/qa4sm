export class UserDataFileDto {
  constructor(public id: string,
              public file: File,
              public file_name: string,
              public owner: number,
              public dataset: number,
              public version: number,
              public variable: number,
              public all_variables: {name: string, standard_name: string, long_name: string, units: string}[],
              public upload_date: Date,
              public is_used_in_validation: boolean,
              public file_size: number,
              public owner_validation_list: {val_id: string, val_name: string}[],
              public number_of_other_users_validations: number,
              public metadata_submitted: boolean,
              public user_groups: number[]
              ) {
  }
}

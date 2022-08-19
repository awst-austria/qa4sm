export class UserDataFileDto {
  constructor(public id: string,
              public file: File,
              public file_name: string,
              public owner: number,
              public dataset: number,
              public version: number,
              public variable: number) {
  }
}

export class UserDataFileDto {
  constructor(public id: number,
              public file: File,
              public file_name: string,
              public owner: number,
              public dataset: number,
              public version: number,
              public variable: number) {
  }
}

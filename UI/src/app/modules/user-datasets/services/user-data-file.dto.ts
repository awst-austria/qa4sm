export class UserDataFileDto {
  constructor(public id: number,
              public file: File,
              public file_name: string,
              public owner: number) {
  }
}
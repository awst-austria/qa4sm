export class CopiedValidationrunDto{
  constructor(public id: number,
              public copied_run: string,
              public used_by_user: number,
              public original_run: string) {
  }
}


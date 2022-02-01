export class ExistingValidationDto{
  // tslint:disable:variable-name
  constructor(public is_there_validation: boolean,
              public val_id: string,
              public belongs_to_user: boolean,
              public is_published: boolean){
  }
}

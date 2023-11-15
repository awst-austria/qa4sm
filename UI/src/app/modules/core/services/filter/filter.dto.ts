export class FilterDto {
  constructor(public id: number,
              public name: string,
              public description: string,
              public help_text: string,
              public parameterised: boolean,
              public dialog_name: string,
              public default_parameter: string,
              public to_include: string,
              public to_exclude: string,
              public default_set_active: boolean,
              public readonly: boolean,
              ) {
  }
}

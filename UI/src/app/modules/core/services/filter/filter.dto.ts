export class FilterDto {
  constructor(public id: number,
              public name: string,
              public description: string,
              public help_text: string,
              public parameterised: boolean,
              public dialog_name: string,
              public default_parameter: string,
              public disable_filter: number,) {
  }
}

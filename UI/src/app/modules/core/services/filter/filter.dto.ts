export class FilterDto {
  constructor(public id: number,
              public name: string,
              public description: string,
              public help_text: string,
              public parameterised: boolean,
              public dialog_name: string,
              public default_parameter: string,
              public threshold: boolean,
              public default_threshold: number,
              public min_threshold: number,
              public max_threshold: number,
              public to_include: string,
              public disable_filter: number,) {
  }
}

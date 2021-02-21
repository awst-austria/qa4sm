export class DatasetVariableDto{
constructor(public id: number,
            public short_name: string,
            public pretty_name: string,
            public help_text: string,
            public min_value: number,
            public max_value: number) {
}
}

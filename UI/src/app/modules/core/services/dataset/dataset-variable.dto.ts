export class DatasetVariableDto{
constructor(public id: number,
            public short_name: string,
            public pretty_name: string,
            public display_name: string,
            public help_text: string,
            public min_value: number,
            public max_value: number,
            public unit: string,
            // depth of the soil layer this variable represents, in metres.
            // Null where depth does not apply, e.g. the CGLS SWI T-values.
            public depth_from?: number,
            public depth_to?: number,
            // 'layer' | 'aggregate' | '' - only 'layer' may take part in a
            // layer merge. Deliberately separate from the depths, so that
            // filling in a missing depth cannot make something mergeable.
            public depth_kind?: string) {
}
}

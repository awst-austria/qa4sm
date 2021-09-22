export class ComparisonDto {
  constructor(public ids: number[],
              public extent: string, // actually not string but python tuple - how?
              public get_intersection: boolean,) {
  }
}

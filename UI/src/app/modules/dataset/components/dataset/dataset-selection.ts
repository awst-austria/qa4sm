export class DatasetSelection{
  constructor(public datasetName:string,
              public datasetId:number,
              public versionId:number,
              public variableId:number,
              public filters?:any[]) {  //TODO: set filter type
  }
}

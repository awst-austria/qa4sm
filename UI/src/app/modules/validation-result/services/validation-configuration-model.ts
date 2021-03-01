export class ValidationConfigurationDto{
  constructor(public datasets: number[],
              public refDataset: number,
              public datasetsVersions: number[],
              public datasetsVariable: number[]){}
}

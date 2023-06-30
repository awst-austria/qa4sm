export class DataManagementGroupsDto{
  constructor(
    public id: number,
    public name: string,
    public permissions: number[],
    public group_owner: number,
    public user_set: number[],
    public custom_datasets: string[]
  ) {
  }
}

import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {DataManagementGroupsDto} from '../../services/data-management-groups.dto';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {BehaviorSubject} from 'rxjs';

@Component({
  selector: 'qa-share-user-data',
  templateUrl: './share-user-data.component.html',
  styleUrls: ['./share-user-data.component.scss']
})
export class ShareUserDataComponent implements OnInit{

  @Input() userDataset: UserDataFileDto;
  @Input() dataManagementGroups: DataManagementGroupsDto[];
  @Output() openShareDataWindow = new EventEmitter<boolean>()

  addToGroupModalWindow = false;
  removeFromGroupWindow = false
  createNewGroupModalWindow = false;
  // shareDataModalWindow = false;


  groupToUpdate: DataManagementGroupsDto
  datasetGroups$: BehaviorSubject<DataManagementGroupsDto[]> =
    new BehaviorSubject<DataManagementGroupsDto[]>([])

  constructor(public userDatasetService: UserDatasetsService) {
  }

  ngOnInit() {
    // this.userDatasetService.doOpenSharingDataWindow.subscribe(open => {
    //   this.shareDataModalWindow = open;
    //   console.log('tryig to open the sharing window')
    // })
    this.datasetGroups$.next(
      this.dataManagementGroups.filter(group => this.userDataset.user_groups.includes(group.id))
    )
  }

  public createGroup(): void{
    this.createNewGroupModalWindow = true;
    this.addToGroupModalWindow = false;
    //   this function will open a group creation form
  }
  public openAddToGroupModalWindow(): void{
    this.addToGroupModalWindow = true;
  }

  public openRemovedGroupModalWindow(): void{
    this.removeFromGroupWindow = true;
  }


  public manageDataInGroup(groupId: number, dataId: string, action: string): void{
    this.userDatasetService.manageDataInManagementGroup(groupId, dataId, action).subscribe(data => {
      console.log(data);
      this.openShareDataWindow.emit(false)
      // this.shareDataModalWindow = false;
    })
  }

}

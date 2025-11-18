import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {DataManagementGroupsDto} from '../../services/data-management-groups.dto';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {BehaviorSubject} from 'rxjs';

@Component({
    selector: 'qa-share-user-data',
    templateUrl: './share-user-data.component.html',
    styleUrls: ['./share-user-data.component.scss'],
    standalone: false
})
export class ShareUserDataComponent implements OnInit, OnChanges{

  @Input() userDataset: UserDataFileDto;
  @Input() dataManagementGroups: DataManagementGroupsDto[];
  @Input() isOpened: boolean;
  @Output() openShareDataWindow = new EventEmitter<boolean>()

  addToGroupView = false;
  deleteGroupView = false;
  removeFromGroupView = false
  createNewGroupModalView = false;
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

  ngOnChanges(changes: SimpleChanges): void{
    if (changes.isOpened && !changes.isOpened.firstChange) {
      if (this.isOpened) {
        this.resetView();
      }
    }
  }

  private resetView(): void{
    this.addToGroupView = false;
    this.deleteGroupView = false;
    this.removeFromGroupView = false
    this.createNewGroupModalView = false;
  }

  public createGroup(): void{
    this.createNewGroupModalView = true;
    // this.addToGroupView = false;
    // this.deleteGroupView = false;
    //   this function will open a group creation form
  }
  public openAddToGroupModalWindow(): void{
    this.addToGroupView = true;
  }

  public openRemovedGroupModalWindow(): void{
    this.removeFromGroupView = true;
  }


  // todo: this one is to be still developed
  public manageDataInGroup(groupId: number, dataId: string, action: string): void{
    this.userDatasetService.manageDataInManagementGroup(groupId, dataId, action)
      .subscribe(data => {
      this.openShareDataWindow.emit(false)
      // this.shareDataModalWindow = false;
    })
  }

  public removeGroup(): void{
    // console.log('I am trying to remove this group')
  }

}

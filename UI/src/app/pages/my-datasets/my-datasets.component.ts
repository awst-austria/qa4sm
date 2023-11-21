import {Component, OnInit} from '@angular/core';
import {UserDatasetsService} from '../../modules/user-datasets/services/user-datasets.service';
import {Observable} from 'rxjs';
import {UserDataFileDto} from '../../modules/user-datasets/services/user-data-file.dto';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {DataManagementGroupsDto} from '../../modules/user-datasets/services/data-management-groups.dto';
import {SettingsService} from '../../modules/core/services/global/settings.service';

@Component({
  selector: 'qa-my-datasets',
  templateUrl: './my-datasets.component.html',
  styleUrls: ['./my-datasets.component.scss']
})
export class MyDatasetsComponent implements OnInit {
  // userDatasets = [];
  constructor(private userDatasetService: UserDatasetsService,
              public authService: AuthService,
              private settingsService: SettingsService,) { }
  userDatasets$: Observable<UserDataFileDto[]>;
  dataManagementGroups$: Observable<DataManagementGroupsDto[]>;
  readMore = false;
  hasNoSpaceLimit: boolean;
  hasNoSpaceAssigned: boolean;
  sharingWindowOpened = false;
  maintenanceMode = false;
  // userDatasetToEdit: UserDataFileDto;

  pageStyle ={
    'max-width': `${this.authService.currentUser.is_staff ? '85rem' : '70rem'}`
  }

  ngOnInit(): void {
    this.settingsService.getAllSettings().subscribe(setting => {
      this.maintenanceMode = setting[0].maintenance_mode;
    });
    this.userDatasets$ = this.userDatasetService.getUserDataList();
    this.refreshUserData();
    this.hasNoSpaceLimit = !this.authService.currentUser.space_limit_value;
    this.hasNoSpaceAssigned = this.authService.currentUser.space_limit_value === 1;
    this.dataManagementGroups$ = this.userDatasetService.getDataManagementGroups()
    this.dataManagementGroups$.subscribe(data =>{
    })
  }

  toggleReadMore(): void{
    this.readMore = !this.readMore;
  }

  refreshUserData(): void{
    this.userDatasetService.doRefresh.subscribe(value => {
      if (value){
        this.userDatasets$ = this.userDatasetService.getUserDataList();
      }
    });
  }

  getLimitMessage(): string{
    let message;
    this.hasNoSpaceLimit ?
      message = 'You have no space limit for your data.' :
      message = `You can use up to ${this.authService.currentUser.space_limit_value / Math.pow(10, 9)}
      GB space for your data. You still have ${this.userDatasetService.getTheSizeInProperUnits(this.authService.currentUser.space_left)} available.`;

    return message;
  }

}

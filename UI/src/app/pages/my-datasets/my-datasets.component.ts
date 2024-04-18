import {Component, OnInit} from '@angular/core';
import {UserDatasetsService} from '../../modules/user-datasets/services/user-datasets.service';
import {EMPTY, Observable} from 'rxjs';
import {AuthService} from '../../modules/core/services/auth/auth.service';
import {DataManagementGroupsDto} from '../../modules/user-datasets/services/data-management-groups.dto';
import {SettingsService} from '../../modules/core/services/global/settings.service';
import {catchError} from 'rxjs/operators';

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
  //
  // userDatasets$: Observable<UserDataFileDto[]>;
  dataManagementGroups$: Observable<DataManagementGroupsDto[]>;
  readMore = false;
  hasNoSpaceLimit: boolean;
  hasNoSpaceAssigned: boolean;
  sharingWindowOpened = false; // do not remove this one for now
  maintenanceMode = false;
  datasetFetchError = false;
  settingsError = false;
  // userDatasetToEdit: UserDataFileDto;

  pageStyle ={
    'max-width': `${this.authService.currentUser.is_staff ? '85rem' : '70rem'}`
  }

  userDatasets$ = this.userDatasetService.getUserDataList()
    .pipe(
      catchError(() => this.datasetsFetchErrorHandling())
    );

  ngOnInit(): void {
    // getAllSettings is used to check if there is a maintenance mode on, if we are not able to define if the mode is on
    // or not, we should prevent from uploading datasets, just in case.
    this.settingsService.getAllSettings()
      .pipe(
        catchError(() => {
          this.settingsError = true;
          return EMPTY;
        })
      )
      .subscribe(setting => {
      this.maintenanceMode = setting[0].maintenance_mode;
    });
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
        this.userDatasets$ = this.userDatasetService.getUserDataList()
          .pipe(
            catchError(() => this.datasetsFetchErrorHandling())
          );
      }
    });
  }

  datasetsFetchErrorHandling(): Observable<never>{
    this.datasetFetchError = true;
    return EMPTY
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

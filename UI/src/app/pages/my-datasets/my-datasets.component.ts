import {Component, OnInit} from '@angular/core';
import {UserDatasetsService} from '../../modules/user-datasets/services/user-datasets.service';
import {Observable} from 'rxjs';
import {UserDataFileDto} from '../../modules/user-datasets/services/user-data-file.dto';
import {AuthService} from '../../modules/core/services/auth/auth.service';

@Component({
  selector: 'qa-my-datasets',
  templateUrl: './my-datasets.component.html',
  styleUrls: ['./my-datasets.component.scss']
})
export class MyDatasetsComponent implements OnInit {
  // userDatasets = [];
  constructor(private userDatasetService: UserDatasetsService,
              public authService: AuthService) { }
  userDatasets$: Observable<UserDataFileDto[]>;
  readMore = false;
  hasNoSpaceLimit: boolean;
  hasNoSpaceAssigned: boolean;

  ngOnInit(): void {
    this.userDatasets$ = this.userDatasetService.getUserDataList();
    this.userDatasetService.doRefresh.subscribe(value => {
      if (value){
        this.userDatasets$ = this.userDatasetService.getUserDataList();
      }
    });
    this.hasNoSpaceLimit = !this.authService.currentUser.space_limit_value;
    this.hasNoSpaceAssigned = this.authService.currentUser.space_limit_value === 1;
  }

  toggleReadMore(): void{
    this.readMore = !this.readMore;
  }

  getLimitMessage(): string{
    let message;
    this.hasNoSpaceLimit ?
      message = 'You have no space limit for your data.' :
      message = `You can use up to ${this.authService.currentUser.space_limit_value / Math.pow(10, 9)}
      GB space for your data.`;

    return message;
  }

  getSpaceLeft(): number{
    return Math.round((1 - this.authService.currentUser.space_left / this.authService.currentUser.space_limit_value) * 100);
  }

}

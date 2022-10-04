import {Component, OnInit} from '@angular/core';
import {UserDatasetsService} from '../../modules/user-datasets/services/user-datasets.service';
import {Observable} from 'rxjs';
import {UserDataFileDto} from '../../modules/user-datasets/services/user-data-file.dto';

@Component({
  selector: 'qa-my-datasets',
  templateUrl: './my-datasets.component.html',
  styleUrls: ['./my-datasets.component.scss']
})
export class MyDatasetsComponent implements OnInit {
  // userDatasets = [];
  constructor(private userDatasetService: UserDatasetsService) { }
  userDatasets$: Observable<UserDataFileDto[]>;
  readMore = false;

  ngOnInit(): void {
    this.userDatasets$ = this.userDatasetService.getUserDataList();
    this.userDatasetService.doRefresh.subscribe(value => {
      if (value){
        this.userDatasets$ = this.userDatasetService.getUserDataList();
      }
    });
    this.userDatasets$.subscribe(data => {
      console.log(data);
    },
      error => (errorData) => {
      console.log(errorData);
    });
  }

  toggleReadMore(): void{
    this.readMore = !this.readMore;
  }

}

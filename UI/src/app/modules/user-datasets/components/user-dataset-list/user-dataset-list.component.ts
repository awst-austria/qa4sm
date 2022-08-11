import {Component, Input, OnInit} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {UserDatasetsService} from '../../services/user-datasets.service';

@Component({
  selector: 'qa-user-dataset-list',
  templateUrl: './user-dataset-list.component.html',
  styleUrls: ['./user-dataset-list.component.scss']
})
export class UserDatasetListComponent implements OnInit {

  @Input() userDatasetList: UserDataFileDto[];

  constructor(private userDatasetService: UserDatasetsService) { }

  ngOnInit(): void {
  }
  removeDataset(datasetId): void{
    if (!confirm('Do you really want to delete the dataset?')) {
      return;
    }
    this.userDatasetService.deleteUserData(datasetId).subscribe(() => {
      this.userDatasetService.refresh.next(true);
    });
  }
}

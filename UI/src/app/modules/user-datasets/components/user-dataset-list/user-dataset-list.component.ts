import {Component, Input, OnInit} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';

@Component({
  selector: 'qa-user-dataset-list',
  templateUrl: './user-dataset-list.component.html',
  styleUrls: ['./user-dataset-list.component.scss']
})
export class UserDatasetListComponent implements OnInit {

  @Input() userDatasetList: UserDataFileDto[];

  constructor() { }

  ngOnInit(): void {
  }
  removeDataset(datasetId): void{
    console.log(datasetId);
  }
}

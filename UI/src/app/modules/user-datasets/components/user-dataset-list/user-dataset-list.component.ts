import {Component, Input, OnInit} from '@angular/core';
import {UserDataFileDto} from '../../services/user-data-file.dto';
import {UserDatasetsService} from '../../services/user-datasets.service';
import {DatasetService} from '../../../core/services/dataset/dataset.service';
import {BehaviorSubject, Observable} from 'rxjs';
import {DatasetDto} from '../../../core/services/dataset/dataset.dto';
import {DatasetVersionService} from '../../../core/services/dataset/dataset-version.service';
import {DatasetVersionDto} from '../../../core/services/dataset/dataset-version.dto';
import {DatasetVariableService} from '../../../core/services/dataset/dataset-variable.service';
import {DatasetVariableDto} from '../../../core/services/dataset/dataset-variable.dto';

@Component({
  selector: 'qa-user-dataset-list',
  templateUrl: './user-dataset-list.component.html',
  styleUrls: ['./user-dataset-list.component.scss']
})
export class UserDatasetListComponent implements OnInit {

  @Input() userDatasetList: UserDataFileDto[];
  chosenVariableName: BehaviorSubject<{variable: string, standard_name: string, long_name: string}>;
  editVariable: BehaviorSubject<boolean> = new BehaviorSubject(false);
  chosenLonName: BehaviorSubject<{name: string}>;
  editLonName: BehaviorSubject<boolean> = new BehaviorSubject(false);
  chosenLatName: BehaviorSubject<{name: string}>;
  editLatName: BehaviorSubject<boolean> = new BehaviorSubject(false);
  chosenTimeName: BehaviorSubject<{name: string}>;
  editTimeName: BehaviorSubject<boolean> = new BehaviorSubject(false);

  constructor(private userDatasetService: UserDatasetsService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService) { }

  ngOnInit(): void {
    console.log(this.userDatasetList);
  }
  removeDataset(dataFileId: string): void{
    if (!confirm('Do you really want to delete the dataset?')) {
      return;
    }
    this.userDatasetService.deleteUserData(dataFileId).subscribe(() => {
      this.userDatasetService.refresh.next(true);
    });
  }

  getDataset(datasetId): Observable<DatasetDto>{
    return this.datasetService.getDatasetById(datasetId);
  }

  getDatasetVersion(versionId): Observable<DatasetVersionDto>{
    return this.datasetVersionService.getVersionById(versionId);
  }

  getDatasetVariable(variableId): Observable<DatasetVariableDto>{
    return this.datasetVariableService.getVariableById(variableId);
  }

  testDataset(dataFileId): void{
    this.userDatasetService.testDataset(dataFileId).subscribe(data => {
      console.log(data);
    });
  }

  updateMetdata(userDataId): void{
    console.log('Monika');
  }

}

import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/validation-result/services/validationrun.dto';
import {ValidationrunService} from '../../modules/validation-result/services/validationrun.service';
import {DatasetDto} from '../../modules/dataset/services/dataset.dto';
import {DatasetService} from '../../modules/dataset/services/dataset.service';
import {DatasetVersionDto} from '../../modules/dataset/services/dataset-version.dto';
import {DatasetVersionService} from '../../modules/dataset/services/dataset-version.service';
import {DatasetVariableDto} from '../../modules/dataset/services/dataset-variable.dto';
import {DatasetVariableService} from '../../modules/dataset/services/dataset-variable.service';

@Component({
  selector: 'qa-published-validations',
  templateUrl: './published-validations.component.html',
  styleUrls: ['./published-validations.component.scss']
})
export class PublishedValidationsComponent implements OnInit {
  publishedValidation$: Observable<ValidationrunDto[]>;
  datasets?: DatasetDto[] = [];
  versions?: DatasetVersionDto[] = [];
  variables?: DatasetVariableDto[] = [];

  constructor(private validationrunService: ValidationrunService,
              private datasetService: DatasetService,
              private datasetVersionService: DatasetVersionService,
              private datasetVariableService: DatasetVariableService) {
    // this.getAllDatasets();
  }

  ngOnInit(): void {
    this.publishedValidation$ = this.validationrunService.getPublishedValidationruns();
    this.getDatasetsInfo();

  }

  getDatasetsInfo(){
    this.getAllDatasets(this.datasets);
    this.getAllVersions(this.versions);
    this.getAllVariables(this.variables);
  }

  private getAllDatasets(targetArray: DatasetDto[]) {
    this.datasetService.getAllDatasets().subscribe(datasets => {
      datasets.forEach(dataset => {
        targetArray.push(dataset);
      });
    });
  }

  private getAllVersions(targetArray: DatasetVersionDto[]) {
    this.datasetVersionService.getAllVersions().subscribe(versions => {
      versions.forEach(version => {
        targetArray.push(version);
      });
    });
  }

  private getAllVariables(targetArray: DatasetVariableDto[]) {
    this.datasetVariableService.getAllVariables().subscribe(variables => {
      variables.forEach(variable => {
        targetArray.push(variable);
      });
    });
  }

}

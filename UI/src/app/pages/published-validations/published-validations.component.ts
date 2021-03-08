import {Component, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {ValidationrunDto} from '../../modules/validation-result/services/validationrun.dto';
import {ValidationrunService} from '../../modules/validation-result/services/validationrun.service';
import {DatasetDto} from '../../modules/core/services/dataset/dataset.dto';
import {DatasetVersionDto} from '../../modules/core/services/dataset/dataset-version.dto';
import {DatasetVariableDto} from '../../modules/core/services/dataset/dataset-variable.dto';

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

  constructor(private validationrunService: ValidationrunService) {
  }

  ngOnInit(): void {
    this.publishedValidation$ = this.validationrunService.getPublishedValidationruns();
    this.getDatasetsInfo();

  }

  getDatasetsInfo(){
    this.validationrunService.getAllDatasets(this.datasets);
    this.validationrunService.getAllVersions(this.versions);
    // this.validationrunService.getAllVariables(this.variables);
  }
}
